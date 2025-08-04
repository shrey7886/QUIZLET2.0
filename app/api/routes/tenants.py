"""
Tenant Management API Routes
Handles multitenant operations for Quizlet AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid

from app.core.multitenant_config import (
    TenantManager, 
    get_db, 
    generate_tenant_id, 
    validate_tenant_id,
    set_tenant_context
)
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/tenants", tags=["tenants"])

# Pydantic models for tenant operations
class TenantCreate(BaseModel):
    tenant_name: str
    owner_email: str
    owner_username: Optional[str] = None

class TenantResponse(BaseModel):
    tenant_id: str
    tenant_name: str
    schema_created: bool
    admin_user_created: bool
    admin_email: str
    temp_password: str

class TenantInfo(BaseModel):
    tenant_id: str
    tenant_name: str
    user_count: int
    quiz_count: int
    flashcard_count: int

class TenantStats(BaseModel):
    users_count: int
    quizzes_count: int
    questions_count: int
    flashcards_count: int
    flashcard_decks_count: int

@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tenant with isolated schema and admin user
    """
    try:
        # Generate unique tenant ID
        tenant_id = generate_tenant_id()
        
        # Create tenant with initial setup
        result = await TenantManager.create_tenant(
            tenant_id=tenant_id,
            tenant_name=tenant_data.tenant_name,
            owner_email=tenant_data.owner_email
        )
        
        return TenantResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant: {str(e)}"
        )

@router.get("/", response_model=List[str])
async def list_tenants(
    db: Session = Depends(get_db)
):
    """
    List all tenant schemas (admin only)
    """
    try:
        tenants = TenantManager.list_all_tenants()
        return tenants
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tenants: {str(e)}"
        )

@router.get("/{tenant_id}/stats", response_model=TenantStats)
async def get_tenant_stats(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific tenant
    """
    if not validate_tenant_id(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format"
        )
    
    try:
        stats = TenantManager.get_tenant_stats(tenant_id)
        return TenantStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tenant stats: {str(e)}"
        )

@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a tenant and all its data (admin only)
    """
    if not validate_tenant_id(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format"
        )
    
    try:
        success = await TenantManager.delete_tenant(tenant_id)
        if success:
            return {"message": f"Tenant {tenant_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete tenant"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant: {str(e)}"
        )

@router.post("/{tenant_id}/users")
async def create_tenant_user(
    tenant_id: str,
    user_data: dict,
    db: Session = Depends(get_db)
):
    """
    Create a new user within a specific tenant
    """
    if not validate_tenant_id(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format"
        )
    
    try:
        # Set tenant context for this operation
        set_tenant_context(tenant_id)
        
        # Create user in tenant schema
        from app.core.auth import get_password_hash
        
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=get_password_hash(user_data["password"]),
            tenant_id=tenant_id,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {"message": "User created successfully", "user_id": user.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/{tenant_id}/users")
async def list_tenant_users(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    List all users within a specific tenant
    """
    if not validate_tenant_id(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format"
        )
    
    try:
        # Set tenant context
        set_tenant_context(tenant_id)
        
        users = db.query(User).filter(User.tenant_id == tenant_id).all()
        return [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at
            }
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

# Middleware to extract tenant from headers
async def get_tenant_from_header(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
) -> Optional[str]:
    """Extract tenant ID from request header"""
    if x_tenant_id and validate_tenant_id(x_tenant_id):
        set_tenant_context(x_tenant_id)
        return x_tenant_id
    return None 
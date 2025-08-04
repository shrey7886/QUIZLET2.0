"""
Multitenant Database Configuration for Quizlet AI
Supports multiple tenants with schema-based isolation
"""

import os
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextvars import ContextVar
from fastapi import Depends, HTTPException, status

# Context variable to store current tenant
tenant_context: ContextVar[Optional[str]] = ContextVar('tenant', default=None)

class MultitenantDatabase:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        self.tenant_schemas: Dict[str, bool] = {}
        
        # Only initialize if NEON_DATABASE_URL is set
        neon_url = os.getenv("NEON_DATABASE_URL")
        if neon_url:
            self._initialize_engine(neon_url)
        else:
            print("⚠️  NEON_DATABASE_URL not set. Using local SQLite for development.")

    def _initialize_engine(self, neon_url: str):
        """Initialize the database engine with connection pooling"""
        if not neon_url:
            return

        # Create engine with optimized settings for multitenancy
        self.engine = create_engine(
            neon_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            # Schema search path for multitenancy
            connect_args={
                "options": "-c search_path=public,shared"
            }
        )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_tenant_schema(self, tenant_id: str) -> str:
        """Get schema name for a tenant"""
        return f"tenant_{tenant_id.replace('-', '_')}"

    async def create_tenant_schema(self, tenant_id: str) -> bool:
        """Create a new tenant schema"""
        if not self.engine:
            return False
            
        schema_name = self.get_tenant_schema(tenant_id)

        if schema_name in self.tenant_schemas:
            return True

        try:
            with self.engine.connect() as conn:
                # Create schema
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

                # Set search path for this connection
                conn.execute(text(f"SET search_path TO {schema_name}, public"))

                # Create tables in tenant schema
                metadata = MetaData(schema=schema_name)
                # Import and create all models in tenant schema
                from app.models import user, quiz, flashcards, chat, analytics

                # Create tables
                self.Base.metadata.create_all(bind=conn, schema=schema_name)

                conn.commit()
                self.tenant_schemas[schema_name] = True

                print(f"✅ Created tenant schema: {schema_name}")
                return True

        except Exception as e:
            print(f"❌ Error creating tenant schema {schema_name}: {e}")
            return False

    async def delete_tenant_schema(self, tenant_id: str) -> bool:
        """Delete a tenant schema and all its data"""
        if not self.engine:
            return False
            
        schema_name = self.get_tenant_schema(tenant_id)

        try:
            with self.engine.connect() as conn:
                # Drop schema and all its contents
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
                conn.commit()

                if schema_name in self.tenant_schemas:
                    del self.tenant_schemas[schema_name]

                print(f"✅ Deleted tenant schema: {schema_name}")
                return True

        except Exception as e:
            print(f"❌ Error deleting tenant schema {schema_name}: {e}")
            return False

    def get_session(self, tenant_id: Optional[str] = None) -> Session:
        """Get database session for a specific tenant"""
        if not self.SessionLocal:
            # Fallback to local database for development
            from app.core.database import get_db
            return next(get_db())
            
        session = self.SessionLocal()
        
        if tenant_id:
            schema_name = self.get_tenant_schema(tenant_id)
            session.execute(text(f"SET search_path TO {schema_name}, public"))
        
        return session

    def list_tenants(self) -> list:
        """List all tenant schemas"""
        if not self.engine:
            return []
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name LIKE 'tenant_%'
                """))
                return [row[0] for row in result]
        except Exception as e:
            print(f"❌ Error listing tenants: {e}")
            return []

# Global multitenant database instance
multitenant_db = MultitenantDatabase()

def get_current_tenant() -> Optional[str]:
    """Get current tenant from context"""
    return tenant_context.get()

def get_db(tenant_id: Optional[str] = Depends(get_current_tenant)) -> Session:
    """Dependency to get database session with tenant context"""
    if multitenant_db.SessionLocal:
        return multitenant_db.get_session(tenant_id)
    else:
        # Fallback to local database for development
        from app.core.database import get_db
        return next(get_db())

class TenantManager:
    @staticmethod
    async def create_tenant(tenant_id: str, tenant_name: str, owner_email: str) -> Dict[str, Any]:
        """Create a new tenant with schema and admin user"""
        try:
            # Create tenant schema
            schema_created = await multitenant_db.create_tenant_schema(tenant_id)
            
            if not schema_created:
                raise Exception("Failed to create tenant schema")

            # Create admin user in tenant schema
            admin_created = False
            temp_password = None
            
            if multitenant_db.SessionLocal:
                # Create admin user in tenant schema
                from app.core.auth import get_password_hash
                from app.models.user import User
                
                session = multitenant_db.get_session(tenant_id)
                temp_password = str(uuid.uuid4())[:8]
                
                admin_user = User(
                    email=owner_email,
                    username=owner_email.split('@')[0],
                    hashed_password=get_password_hash(temp_password),
                    is_active=True,
                    is_admin=True,
                    tenant_id=tenant_id
                )
                
                session.add(admin_user)
                session.commit()
                session.close()
                admin_created = True

            return {
                "tenant_id": tenant_id,
                "tenant_name": tenant_name,
                "schema_created": schema_created,
                "admin_user_created": admin_created,
                "admin_email": owner_email,
                "temp_password": temp_password or "N/A"
            }

        except Exception as e:
            print(f"❌ Error creating tenant: {e}")
            raise

    @staticmethod
    async def delete_tenant(tenant_id: str) -> bool:
        """Delete a tenant and all its data"""
        return await multitenant_db.delete_tenant_schema(tenant_id)

    @staticmethod
    def list_all_tenants() -> list:
        """List all tenant schemas"""
        return multitenant_db.list_tenants()

    @staticmethod
    def get_tenant_stats(tenant_id: str) -> Dict[str, Any]:
        """Get statistics for a specific tenant"""
        if not multitenant_db.engine:
            return {
                "users_count": 0,
                "quizzes_count": 0,
                "questions_count": 0,
                "flashcards_count": 0,
                "flashcard_decks_count": 0
            }
            
        try:
            schema_name = multitenant_db.get_tenant_schema(tenant_id)
            
            with multitenant_db.engine.connect() as conn:
                # Set search path to tenant schema
                conn.execute(text(f"SET search_path TO {schema_name}, public"))
                
                # Get counts for different tables
                stats = {}
                
                tables = ['users', 'quizzes', 'questions', 'flashcards', 'flashcard_decks']
                for table in tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        stats[f"{table.replace('_', '')}_count"] = count
                    except:
                        stats[f"{table.replace('_', '')}_count"] = 0
                
                return stats

        except Exception as e:
            print(f"❌ Error getting tenant stats: {e}")
            return {
                "users_count": 0,
                "quizzes_count": 0,
                "questions_count": 0,
                "flashcards_count": 0,
                "flashcard_decks_count": 0
            }

def set_tenant_context(tenant_id: str):
    """Set tenant context for current request"""
    tenant_context.set(tenant_id)

def generate_tenant_id() -> str:
    """Generate a unique tenant ID"""
    return str(uuid.uuid4())

def validate_tenant_id(tenant_id: str) -> bool:
    """Validate tenant ID format"""
    try:
        uuid.UUID(tenant_id)
        return True
    except ValueError:
        return False 
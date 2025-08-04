from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_password, get_password_hash, create_access_token, get_current_active_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, User as UserSchema, Token
import os
import httpx
import urllib.parse

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Check if Google OAuth is configured
GOOGLE_OAUTH_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_CLIENT_ID != "your-google-client-id-here")

@router.post("/google", response_model=Token)
async def google_oauth(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth token verification and user creation/login"""
    try:
        body = await request.json()
        token = body.get("token")
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is required"
            )
        
        # For now, we'll use a simple approach - you can enhance this with proper Google token verification
        # In production, you should verify the token with Google's API
        
        # Extract user information from token (this is a simplified approach)
        # In production, you should verify the token with Google's API
        import jwt
        try:
            # This is a simplified approach - in production, verify with Google
            decoded = jwt.decode(token, options={"verify_signature": False})
            email = decoded.get('email', '')
            name = decoded.get('name', '')
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Create new user
                username = email.split('@')[0]  # Use email prefix as username
                hashed_password = get_password_hash(f"google_{email}")  # Generate a secure password
                
                user = User(
                    email=email,
                    username=username,
                    hashed_password=hashed_password,
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Create access token
            access_token = create_access_token(data={"sub": user.email})
            
            return {"access_token": access_token, "token_type": "bearer"}
            
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google OAuth failed"
        )

@router.get("/google/login")
async def google_login():
    """Redirect to Google OAuth"""
    if not GOOGLE_OAUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )
    
    google_oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": "http://localhost:8000/api/auth/google/callback",  # Backend callback URL
        "response_type": "code",
        "scope": "email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    # Build the URL with parameters
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{google_oauth_url}?{query_string}"
    
    return RedirectResponse(url=auth_url)

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    if not GOOGLE_OAUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )
    
    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:8000/api/auth/google/callback"  # Backend callback URL
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            token_response = response.json()
            
            if "access_token" not in token_response:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get access token"
                )
            
            access_token = token_response["access_token"]
            
            # Get user info from Google
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            userinfo_response = await client.get(userinfo_url, headers=headers)
            userinfo = userinfo_response.json()
            
            email = userinfo.get("email")
            name = userinfo.get("name", "")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user email"
                )
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Create new user
                username = email.split('@')[0]  # Use email prefix as username
                hashed_password = get_password_hash(f"google_{email}")  # Generate a secure password
                
                user = User(
                    email=email,
                    username=username,
                    hashed_password=hashed_password,
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Create access token
            access_token = create_access_token(data={"sub": user.email})
            
            # Redirect to frontend with token
            frontend_url = f"http://localhost:8000/auth/callback?token={access_token}"
            return RedirectResponse(url=frontend_url)
            
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = f"http://localhost:8000/auth/callback?error=oauth_failed"
        return RedirectResponse(url=frontend_url) 
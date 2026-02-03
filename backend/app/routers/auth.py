from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import httpx
from app.database import get_db
from app.models import User
from app.schemas import Token, UserResponse
from app.auth import create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login flow"""
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    redirect_uri = f"{settings.backend_url}/api/auth/google/callback"
    
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{google_auth_url}?{query_string}"
    
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"{settings.backend_url}/api/auth/google/callback"
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            })
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code"
                )
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            # Get user info
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )
            
            user_info = userinfo_response.json()
        
        # Find or create user
        result = await db.execute(
            select(User).where(User.google_id == user_info["id"])
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update user info
            user.name = user_info.get("name")
            user.picture = user_info.get("picture")
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = User(
                email=user_info["email"],
                name=user_info.get("name"),
                picture=user_info.get("picture"),
                google_id=user_info["id"],
                is_admin=False  # First user could be admin
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(user)
        
        # Create JWT token
        jwt_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # Redirect to frontend with token
        redirect_url = f"{settings.frontend_url}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout():
    """Logout user (client-side token deletion)"""
    return {"message": "Logged out successfully"}

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import secrets
from typing import Optional
from backend.models.database import get_db_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Two authentic looking mock profiles
MOCK_PROFILES = {
    "techenthusiast99": {
        "reddit_id": "t2_mock_tech99"
    },
    "criticalgamerx": {
        "reddit_id": "t2_mock_gamerx"
    }
}

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db_session)):
    """Authenticates the user silently based on pre-defined mock profiles."""
    username = data.username.lower().strip()
    if username not in MOCK_PROFILES:
        raise HTTPException(status_code=401, detail="Invalid credentials. Cannot reach Reddit servers.")
        
    profile = MOCK_PROFILES[username]
    
    # Store or update user in database
    result = await db.execute(select(User).where(User.reddit_id == profile["reddit_id"]))
    user = result.scalar_one_or_none()
    
    # Fake refresh token
    refresh_token = f"mock_refresh_token_for_{username}_{secrets.token_urlsafe(8)}"
    
    if not user:
        user = User(
            reddit_username=username,
            reddit_id=profile["reddit_id"],
            refresh_token=refresh_token
        )
        db.add(user)
    else:
        user.refresh_token = refresh_token
        user.reddit_username = username
        
    await db.commit()
    await db.refresh(user)
    
    # Create persistent session
    request.session['user_id'] = user.id
    
    # Redirect back to frontend dashboard automatically
    return {"message": "Success", "username": username}


@router.post("/logout")
async def logout(request: Request):
    """Clears the session."""
    request.session.clear()
    return {"message": "Logged out successfully"}


@router.get("/status")
async def auth_status(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Checks if the current session is authenticated."""
    user_id = request.session.get("user_id")
    if not user_id:
        return {"authenticated": False}
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return {"authenticated": False}
        
    return {"authenticated": True, "username": user.reddit_username}


# Fast dependency for other routers
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db_session)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user

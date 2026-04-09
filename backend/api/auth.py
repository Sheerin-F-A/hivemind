from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import secrets
import time
import random
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from nltk.sentiment import SentimentIntensityAnalyzer

from backend.models.database import get_db_session, User, Comment
from backend.services.scraper import scrape_reddit_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

try:
    sia = SentimentIntensityAnalyzer()
except LookupError:
    import nltk
    nltk.download('vader_lexicon', quiet=True)
    sia = SentimentIntensityAnalyzer()

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = None

@router.post("/login")
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db_session)):
    """Authenticates the user by physically scraping their Profile via Playwright."""
    username = data.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    result = await db.execute(select(User).where(User.reddit_username.ilike(username)))
    user = result.scalar_one_or_none()
    
    if not user:
        # Phase 7: Organic Profile Verification
        try:
            import json
            import os
            # If the user exactly typed a name that has a prebuilt fake JSON mock:
            filepath = None
            if os.path.exists(f"{username}.json"):
                filepath = f"{username}.json"
            elif os.path.exists(f"{username.lower()}.json"):
                filepath = f"{username.lower()}.json"
                
            if filepath:
                with open(filepath, "r") as f:
                    profile_comments = json.load(f)
            else:
                # Run the actual scrape hook
                profile_comments = await scrape_reddit_user(username)
        except Exception:
            raise HTTPException(status_code=404, detail="Could not physically reach Reddit profile.")
            
        if not profile_comments:
            raise HTTPException(status_code=404, detail="Reddit user doesn't exist or has 0 public comments!")
            
        # Valid User! Register them.
        user = User(
            reddit_username=username,
            reddit_id=f"organic_u_{username.lower()}",
            refresh_token=f"mock_refresh_token_for_{username}_{secrets.token_urlsafe(8)}"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Inject their public behavioral NLP into their personal SQLite vault
        for c in profile_comments:
            scores = sia.polarity_scores(c["body"])
            compound = scores['compound']
            if compound >= 0.05:
                label = "positive"
            elif compound <= -0.05:
                label = "negative"
            else:
                label = "neutral"
                
                
            db_comment = Comment(
                user_id=user.id,
                comment_id=f"organic_hist_{random.randint(1000,999999)}",
                subreddit=c["subreddit"],
                thread_id="vault_history",
                thread_title=c.get("title", "Organic Personal Account History"),
                body=c["body"],
                created_utc=c.get("timestamp", int(time.time()) - random.randint(100, 300000)),
                score=c["score"],
                sentiment_score=compound,
                sentiment_label=label,
                is_spam=c.get("is_spam", False)
            )
            # Simulating incremental sync (upsert)
            db.add(db_comment)
            
        await db.commit()

    # Create persistent session
    request.session['user_id'] = user.id
    
    return {"message": "Success", "username": user.reddit_username}


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

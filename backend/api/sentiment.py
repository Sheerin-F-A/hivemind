from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.models.database import get_db_session, User, Comment
from backend.api.auth import get_current_user
from datetime import datetime, timedelta
import math

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])

@router.get("/overview")
@router.get("/overview/")
async def get_sentiment_overview(
    query: str = "",
    days: int = 30,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    """
    Aggregates sentiment from the stored generated mock comments.
    """
    cutoff_time = int((datetime.utcnow() - timedelta(days=days)).timestamp())
    
    # Query all dummy comments matching the thread_title (mocking a search proxy)
    stmt = select(Comment).where(
        Comment.user_id == user.id,
        Comment.created_utc >= cutoff_time
    )
    
    if query:
        stmt = stmt.where(Comment.thread_title.ilike(f"%{query}%"))
        
    result = await db.execute(stmt)
    comments = result.scalars().all()
    
    if not comments:
        return {
            "overall_score": 0,
            "overall_label": "Neutral",
            "comments_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
            "content_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
            "history": {"labels": [], "positive": [], "neutral": [], "negative": []}
        }
        
    # Aggregate stats
    pos_count = sum(1 for c in comments if c.sentiment_score and c.sentiment_score > 0.05)
    neg_count = sum(1 for c in comments if c.sentiment_score and c.sentiment_score < -0.05)
    neu_count = len(comments) - pos_count - neg_count
    
    total = len(comments)
    
    # Map score bounds from [-1, 1] to [0, 100] for UI
    avg_raw = sum(c.sentiment_score or 0 for c in comments) / total
    overall_score = int((avg_raw + 1) * 50) 
    
    if overall_score >= 60:
        overall_label = "Positive"
    elif overall_score <= 40:
        overall_label = "Negative"
    else:
        overall_label = "Neutral"
        
    # Simulate historical timeline data points (grouping by day)
    history_groups = {}
    for c in comments:
        dt = datetime.utcfromtimestamp(c.created_utc)
        day_str = dt.strftime("%b %d")
        if day_str not in history_groups:
            history_groups[day_str] = {"pos": 0, "neu": 0, "neg": 0, "total": 0}
            
        history_groups[day_str]["total"] += 1
        if c.sentiment_score and c.sentiment_score > 0.05:
            history_groups[day_str]["pos"] += 1
        elif c.sentiment_score and c.sentiment_score < -0.05:
            history_groups[day_str]["neg"] += 1
        else:
            history_groups[day_str]["neu"] += 1
            
    # Sort and flatten history
    labels = sorted(list(history_groups.keys()))
    pos_hist = [int((history_groups[l]["pos"]/history_groups[l]["total"])*100) for l in labels]
    neu_hist = [int((history_groups[l]["neu"]/history_groups[l]["total"])*100) for l in labels]
    neg_hist = [int((history_groups[l]["neg"]/history_groups[l]["total"])*100) for l in labels]
    
    # Just simulating "content breakdown" as slightly offset for visual flair
    return {
        "overall_score": overall_score,
        "overall_label": overall_label,
        "comments_breakdown": {
            "positive": int((pos_count/total)*100),
            "neutral": int((neu_count/total)*100),
            "negative": int((neg_count/total)*100)
        },
        "content_breakdown": {
            "positive": min(100, int((pos_count/total)*100) + 6),
            "neutral": max(0, int((neu_count/total)*100) - 3),
            "negative": max(0, int((neg_count/total)*100) - 3)
        },
        "history": {
            "labels": labels,
            "positive": pos_hist,
            "neutral": neu_hist,
            "negative": neg_hist
        }
    }

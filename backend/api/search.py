import random
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

from backend.models.database import get_db_session, Comment
from backend.api.auth import get_current_user, User
from backend.services.scraper import scrape_reddit_posts


# Initialize NLTK VADER
try:
    sia = SentimentIntensityAnalyzer()
except LookupError:
    # If not downloaded yet
    nltk.download('vader_lexicon', quiet=True)
    sia = SentimentIntensityAnalyzer()

router = APIRouter(prefix="/api/search", tags=["search"])

def generate_mock_comments(topic: str, persona: str) -> List[dict]:
    """Generates fake Reddit comments tailored to the prompt and the testing persona."""
    
    # Highly positive template options for TechEnthusiast99
    positive_phrases = [
        f"This is the best {topic} announcement I've seen all year! So excited.",
        f"I can't believe how far {topic} has come. Absolutely groundbreaking work here.",
        f"{topic} changed my life for the better. Just incredible engineering.",
        f"Anyone saying {topic} isn't the future is just coping. Amazing stuff.",
        f"I'm all-in on {topic}. The community around this is top-notch!"
    ]
    
    # Highly negative/critical template options for CriticalGamerX
    negative_phrases = [
        f"Ugh, another {topic} cash grab. Why do companies keep doing this?",
        f"{topic} is completely ruined. They took out everything good about it.",
        f"I'm so tired of {topic}. It's a buggy, unoptimized mess.",
        f"Don't pre-order {topic}. The devs clearly rushed it. Huge disappointment.",
        f"Literally unplayable. {topic} has been downhill since 2018."
    ]
    
    # Neutral/Mixed fallback to simulate realism
    mixed_phrases = [
        f"I guess {topic} is okay, but I'll wait for a sale.",
        f"Some good ideas in {topic}, but execution is lacking.",
        f"{topic} is fine. Not terrible, not great."
    ]

    comments = []
    
    # Determine bias based on persona
    if "Enthusiast" in persona:
        pool = positive_phrases * 3 + mixed_phrases # 75% positive
    elif "Critical" in persona:
        pool = negative_phrases * 3 + mixed_phrases # 75% negative
    else:
        pool = positive_phrases + negative_phrases + mixed_phrases
        
    num_comments = random.randint(5, 15)
    
    for i in range(num_comments):
        text = random.choice(pool)
        
        # Calculate sentiment using real ML!
        scores = sia.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
            
        comments.append({
            "comment_id": f"mock_{topic}_{i}_{random.randint(1000,9999)}",
            "subreddit": "technology" if "Enthusiast" in persona else "gaming",
            "thread_id": f"thread_{topic}_{random.randint(1,100)}",
            "thread_title": f"Official Discussion: {topic}",
            "body": text,
            "created_utc": int(time.time()) - random.randint(1000, 2500000),
            "score": random.randint(-5, 120),
            "sentiment_score": compound,
            "sentiment_label": label
        })
        
    return comments


user_last_search_time = {}

@router.post("")
@router.post("/")
async def perform_search(query: str = Query(..., description="The topic to search for"), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)):
    """Simulates querying Reddit for a topic, generates fake comments based on the user's persona, and stores sentiment in DB."""
    
    # 1. Idempotency Check: if data exists for this user and query, just succeed quietly
    stmt = select(Comment).where(Comment.user_id == user.id, Comment.thread_title.ilike(f"%{query}%")).limit(1)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return {
            "status": "success",
            "query": query,
            "persona_used": user.reddit_username,
            "comments_fetched": 0,
            "message": "Data already cached. Fetched directly from SQLite."
        }
        
    # 2. Rate Limiting Check
    now = time.time()
    if user.id in user_last_search_time:
        if now - user_last_search_time[user.id] < 60:
            raise HTTPException(status_code=429, detail="rate limit reached, wait a bit")
    user_last_search_time[user.id] = now
    
    try:
        organic_posts = await scrape_reddit_posts(query, limit=15)
    except Exception as e:
        print(f"Playwright error, falling back: {e}")
        organic_posts = []

    processed_comments = []
    if organic_posts:
        for p in organic_posts:
            scores = sia.polarity_scores(p["body"])
            compound = scores['compound']
            if compound >= 0.05:
                label = "positive"
            elif compound <= -0.05:
                label = "negative"
            else:
                label = "neutral"
                
            p["sentiment_score"] = compound
            p["sentiment_label"] = label
            
            # Simulate real active timestamps for dashboard distribution
            p["created_utc"] = int(time.time()) - random.randint(100, 300000)
            processed_comments.append(p)
    else:
        # Fallback to entirely mocked data if scraper yields 0
        processed_comments = generate_mock_comments(query, user.reddit_username)
    
    new_db_comments = []
    for c_data in processed_comments:
        comment = Comment(
            user_id=user.id,
            comment_id=c_data["comment_id"],
            subreddit=c_data["subreddit"],
            thread_id=c_data["thread_id"],
            thread_title=c_data["thread_title"],
            body=c_data["body"],
            created_utc=c_data["created_utc"],
            score=c_data["score"],
            sentiment_score=c_data["sentiment_score"],
            sentiment_label=c_data["sentiment_label"],
            is_spam=False
        )
        db.add(comment)
        new_db_comments.append(comment)
        
    await db.commit()
    
    return {
        "status": "success",
        "query": query,
        "persona_used": user.reddit_username,
        "comments_fetched": len(new_db_comments),
        "message": f"Successfully simulated fetching {len(new_db_comments)} comments about {query} and ran VADER sentiment analysis."
    }

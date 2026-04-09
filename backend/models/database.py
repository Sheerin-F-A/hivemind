from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.config import settings
from backend.utils.logger import logger

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reddit_username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    reddit_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    access_token: Mapped[Optional[str]] = mapped_column(String)
    refresh_token: Mapped[Optional[str]] = mapped_column(String)
    token_expires_at: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    subreddit: Mapped[str] = mapped_column(String, nullable=False, index=True)
    thread_id: Mapped[str] = mapped_column(String, nullable=False)
    thread_title: Mapped[Optional[str]] = mapped_column(String)
    body: Mapped[str] = mapped_column(String, nullable=False)
    created_utc: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    edited_utc: Mapped[Optional[int]] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer, default=0)
    
    is_spam: Mapped[bool] = mapped_column(Boolean, default=False)
    spam_reason: Mapped[Optional[str]] = mapped_column(String)
    
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)
    sentiment_label: Mapped[Optional[str]] = mapped_column(String, index=True)
    
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="comments")


# Database setup
engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Initializes the database schema."""
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")

async def get_db_session():
    """Dependency to get the database session."""
    async with async_session_maker() as session:
        yield session

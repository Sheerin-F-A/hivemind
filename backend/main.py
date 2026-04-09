from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager

from backend.utils.logger import logger
from backend.config import settings
from backend.api import auth, search, sentiment
from backend.models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database on startup
    await init_db()
    yield

app = FastAPI(
    title="Reddit Hive Mind API",
    description="Backend for the Reddit Hive Mind sentiment vault.",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for OAuth state and login session
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="hivemind_session",
    max_age=14 * 24 * 60 * 60,  # 14 days
    same_site="lax",
    https_only=False, # Set to True in production with HTTPS
)

# Include routers
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(sentiment.router)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "network connection is unstable", "details": str(exc)},
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify backend status."""
    return {"status": "ok", "service": "reddit-hive-mind"}

# Mount frontend files at the root
# Note: we mount the parent repo directory because index.html is there.
# Use html=True so that visiting /dashboard.html just works, and / defaults to index.html
app.mount("/", StaticFiles(directory=".", html=True), name="frontend")

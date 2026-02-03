from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import os

from app.config import settings
from app.database import init_db, async_session_maker
from app.routers import auth, events, scraper
from app.scrapers.scraper_manager import scraper_manager
from app.auth import get_current_user
from app.schemas import UserResponse

# Scheduler for automatic scraping
scheduler = AsyncIOScheduler()


async def scheduled_scrape():
    """Scheduled scraping task"""
    async with async_session_maker() as db:
        try:
            print("Running scheduled scrape...")
            results = await scraper_manager.run_all_scrapers(db)
            print(f"Scheduled scrape completed: {results}")
        except Exception as e:
            print(f"Scheduled scrape error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing database...")
    await init_db()
    print("Database initialized")
    
    # Schedule automatic scraping every 6 hours
    # Note: Initial scrape will run on first scheduled interval
    scheduler.add_job(
        scheduled_scrape,
        IntervalTrigger(hours=6),
        id='auto_scrape',
        name='Automatic Event Scraping',
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started - scraping every 6 hours")
    print("Application started successfully - ready to accept requests")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    print("Application shutdown")


app = FastAPI(
    title="Sydney Events API",
    description="API for scraped Sydney events with Google OAuth authentication",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://*.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(scraper.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current authenticated user"""
    return UserResponse.model_validate(current_user)


# Serve static frontend files (for production deployment)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    # Serve static assets (js, css, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/")
    async def serve_index():
        """Serve the SPA index"""
        return FileResponse(os.path.join(static_dir, "index.html"))
    
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve the SPA for all non-API routes"""
        # Don't serve index.html for API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            return {"detail": "Not found"}
        
        # Try to serve static file first
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fall back to index.html for SPA routing
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "Sydney Events API",
            "docs": "/docs",
            "version": "1.0.0"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

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


async def delayed_initial_scrape():
    """Run initial scrape after a delay to allow app to start"""
    await asyncio.sleep(30)  # Wait 30 seconds for app to fully start
    await scheduled_scrape()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing database...")
    await init_db()
    
    # Schedule automatic scraping every 6 hours
    scheduler.add_job(
        scheduled_scrape,
        IntervalTrigger(hours=6),
        id='auto_scrape',
        name='Automatic Event Scraping',
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started - scraping every 6 hours")
    
    # Run initial scrape in background with delay (don't block startup)
    asyncio.create_task(delayed_initial_scrape())
    print("Application started successfully")
    
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


@app.get("/")
async def root():
    return {
        "message": "Sydney Events API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current authenticated user"""
    return UserResponse.model_validate(current_user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

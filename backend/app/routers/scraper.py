from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.database import get_db
from app.models import ScrapeLog, User
from app.scrapers.scraper_manager import scraper_manager
from app.auth import get_current_user

router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/run")
async def run_scrapers(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger all scrapers (requires authentication)"""
    
    # Run scrapers in foreground for now (background would need separate session)
    results = await scraper_manager.run_all_scrapers(db)
    
    return {
        "message": "Scraping completed",
        "results": results
    }


@router.get("/logs")
async def get_scrape_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent scrape logs (requires authentication)"""
    
    result = await db.execute(
        select(ScrapeLog).order_by(desc(ScrapeLog.started_at)).limit(limit)
    )
    logs = result.scalars().all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "source_name": log.source_name,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "finished_at": log.finished_at.isoformat() if log.finished_at else None,
                "events_found": log.events_found,
                "events_new": log.events_new,
                "events_updated": log.events_updated,
                "events_inactive": log.events_inactive,
                "status": log.status,
                "error_message": log.error_message
            }
            for log in logs
        ]
    }


@router.get("/status")
async def get_scraper_status(db: AsyncSession = Depends(get_db)):
    """Get current scraper status (public endpoint)"""
    
    # Get latest log for each source
    sources = ["Eventbrite", "Meetup", "Sydney Opera House", "Time Out Sydney"]
    status_info = []
    
    for source in sources:
        result = await db.execute(
            select(ScrapeLog)
            .where(ScrapeLog.source_name == source)
            .order_by(desc(ScrapeLog.started_at))
            .limit(1)
        )
        log = result.scalar_one_or_none()
        
        status_info.append({
            "source": source,
            "last_run": log.finished_at.isoformat() if log and log.finished_at else None,
            "status": log.status if log else "never_run",
            "events_found": log.events_found if log else 0
        })
    
    return {"scrapers": status_info}

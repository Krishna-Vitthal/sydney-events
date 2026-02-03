import asyncio
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.scrapers import EventbriteScraper, MeetupScraper, SydneyOperaHouseScraper, TimeOutScraper
from app.models import Event, EventStatus, ScrapeLog
import logging

logger = logging.getLogger(__name__)


class ScraperManager:
    """Manages all event scrapers and database synchronization"""
    
    def __init__(self):
        self.scrapers = [
            EventbriteScraper(),
            MeetupScraper(),
            SydneyOperaHouseScraper(),
            TimeOutScraper(),
        ]
    
    async def run_all_scrapers(self, db: AsyncSession) -> Dict[str, Any]:
        """Run all scrapers and sync with database"""
        results = {
            'total_found': 0,
            'new': 0,
            'updated': 0,
            'inactive': 0,
            'errors': []
        }
        
        all_scraped_urls = set()
        
        for scraper in self.scrapers:
            try:
                # Create scrape log
                log = ScrapeLog(
                    source_name=scraper.source_name,
                    started_at=datetime.utcnow()
                )
                db.add(log)
                await db.flush()
                
                # Run scraper
                events = await scraper.scrape()
                
                # Process events
                scraper_results = await self._process_events(db, events, scraper.source_name)
                
                # Update log
                log.finished_at = datetime.utcnow()
                log.events_found = len(events)
                log.events_new = scraper_results['new']
                log.events_updated = scraper_results['updated']
                log.status = 'completed'
                
                results['total_found'] += len(events)
                results['new'] += scraper_results['new']
                results['updated'] += scraper_results['updated']
                
                # Collect URLs for inactive detection
                for event in events:
                    if event.get('source_url'):
                        all_scraped_urls.add(event['source_url'])
                
                logger.info(f"Completed scraping {scraper.source_name}: {len(events)} events")
                
            except Exception as e:
                error_msg = f"Error in {scraper.source_name}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
                
                if 'log' in locals():
                    log.status = 'error'
                    log.error_message = str(e)
                    log.finished_at = datetime.utcnow()
        
        # Mark inactive events
        inactive_count = await self._mark_inactive_events(db, all_scraped_urls)
        results['inactive'] = inactive_count
        
        await db.commit()
        
        return results
    
    async def _process_events(self, db: AsyncSession, events: List[Dict[str, Any]], source_name: str) -> Dict[str, int]:
        """Process scraped events and sync with database"""
        results = {'new': 0, 'updated': 0}
        
        for event_data in events:
            try:
                source_url = event_data.get('source_url')
                if not source_url:
                    continue
                
                # Check if event exists
                result = await db.execute(
                    select(Event).where(Event.source_url == source_url)
                )
                existing_event = result.scalar_one_or_none()
                
                if existing_event:
                    # Check if content changed
                    if existing_event.content_hash != event_data.get('content_hash'):
                        # Update event
                        for key, value in event_data.items():
                            if hasattr(existing_event, key) and key not in ['id', 'first_seen_at', 'is_imported', 'imported_at', 'imported_by_id', 'import_notes']:
                                setattr(existing_event, key, value)
                        existing_event.status = EventStatus.UPDATED.value
                        existing_event.last_scraped_at = datetime.utcnow()
                        results['updated'] += 1
                    else:
                        # Just update last scraped time
                        existing_event.last_scraped_at = datetime.utcnow()
                        # If it was inactive, mark as updated
                        if existing_event.status == EventStatus.INACTIVE.value:
                            existing_event.status = EventStatus.UPDATED.value
                            results['updated'] += 1
                else:
                    # Create new event
                    new_event = Event(
                        title=event_data.get('title'),
                        date_time=event_data.get('date_time'),
                        date_string=event_data.get('date_string'),
                        venue_name=event_data.get('venue_name'),
                        venue_address=event_data.get('venue_address'),
                        city=event_data.get('city', 'Sydney'),
                        description=event_data.get('description'),
                        category=event_data.get('category'),
                        tags=event_data.get('tags'),
                        image_url=event_data.get('image_url'),
                        source_name=source_name,
                        source_url=source_url,
                        content_hash=event_data.get('content_hash'),
                        status=EventStatus.NEW.value,
                        first_seen_at=datetime.utcnow(),
                        last_scraped_at=datetime.utcnow()
                    )
                    db.add(new_event)
                    results['new'] += 1
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
        
        await db.flush()
        return results
    
    async def _mark_inactive_events(self, db: AsyncSession, active_urls: set) -> int:
        """Mark events as inactive if they're no longer found on source"""
        # Get all active (not inactive, not imported) events
        result = await db.execute(
            select(Event).where(
                Event.status.notin_([EventStatus.INACTIVE.value, EventStatus.IMPORTED.value])
            )
        )
        active_events = result.scalars().all()
        
        inactive_count = 0
        for event in active_events:
            if event.source_url not in active_urls:
                event.status = EventStatus.INACTIVE.value
                inactive_count += 1
        
        return inactive_count


# Global instance
scraper_manager = ScraperManager()

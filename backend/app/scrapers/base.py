from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import aiohttp
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all event scrapers"""
    
    def __init__(self):
        self.source_name: str = "Unknown"
        self.base_url: str = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page and return its HTML content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Failed to fetch {url}: Status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content into BeautifulSoup object"""
        return BeautifulSoup(html, 'lxml')
    
    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events and return a list of event dictionaries"""
        pass
    
    def generate_content_hash(self, event: Dict[str, Any]) -> str:
        """Generate a hash of event content for change detection"""
        content = f"{event.get('title', '')}{event.get('date_string', '')}{event.get('venue_name', '')}{event.get('description', '')}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean and normalize text"""
        if text is None:
            return None
        # Remove extra whitespace and normalize
        return ' '.join(text.split()).strip()
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Try to parse a date string into a datetime object"""
        if not date_str:
            return None
            
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%d %b %Y %H:%M",
            "%d %B %Y %H:%M",
            "%d %b %Y",
            "%d %B %Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None

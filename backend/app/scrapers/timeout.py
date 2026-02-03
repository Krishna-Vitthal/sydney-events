from typing import List, Dict, Any
from datetime import datetime
import re
import json
from app.scrapers.base import BaseScraper, logger


class TimeOutScraper(BaseScraper):
    """Scraper for Time Out Sydney events"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "Time Out Sydney"
        self.base_url = "https://www.timeout.com/sydney/things-to-do/things-to-do-in-sydney-this-week"
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Time Out Sydney"""
        events = []
        
        try:
            # Try main events page
            html = await self.fetch_page(self.base_url)
            if not html:
                # Try alternate URL
                html = await self.fetch_page("https://www.timeout.com/sydney/things-to-do")
            
            if not html:
                logger.warning("Failed to fetch Time Out Sydney page")
                return events
            
            soup = self.parse_html(html)
            
            # Look for JSON-LD data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') == 'ItemList':
                            items = data.get('itemListElement', [])
                            for item in items:
                                if item.get('@type') == 'ListItem':
                                    item_data = item.get('item', {})
                                    event = self._parse_list_item(item_data)
                                    if event:
                                        events.append(event)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Find article cards
            article_cards = soup.find_all('article')
            if not article_cards:
                article_cards = soup.find_all('div', class_=re.compile(r'card|article|listing'))
            
            for card in article_cards[:30]:
                event = self._parse_event_card(card)
                if event and event.get('source_url') not in [e.get('source_url') for e in events]:
                    events.append(event)
            
            logger.info(f"Time Out Sydney: Scraped {len(events)} events")
            
        except Exception as e:
            logger.error(f"Time Out Sydney scraping error: {str(e)}")
        
        return events
    
    def _parse_list_item(self, data: Dict) -> Dict[str, Any]:
        """Parse a list item from JSON-LD"""
        try:
            event = {
                'title': self.clean_text(data.get('name', '')),
                'date_string': None,
                'date_time': None,
                'venue_name': None,
                'venue_address': None,
                'city': 'Sydney',
                'description': self.clean_text(data.get('description', ''))[:500] if data.get('description') else None,
                'category': data.get('@type', ''),
                'tags': None,
                'image_url': data.get('image', ''),
                'source_name': self.source_name,
                'source_url': data.get('url', ''),
            }
            
            if event['title'] and event['source_url']:
                event['content_hash'] = self.generate_content_hash(event)
                return event
                
        except Exception as e:
            logger.error(f"Error parsing Time Out list item: {e}")
        
        return None
    
    def _parse_event_card(self, card) -> Dict[str, Any]:
        """Parse an event card HTML element"""
        try:
            # Get title
            title_elem = card.find('h2') or card.find('h3') or card.find(class_=re.compile(r'title|heading|name'))
            title = self.clean_text(title_elem.get_text()) if title_elem else None
            
            # Get link
            link_elem = card.find('a', href=True)
            source_url = link_elem['href'] if link_elem else None
            
            if source_url and not source_url.startswith('http'):
                source_url = f"https://www.timeout.com{source_url}"
            
            # Get description
            desc_elem = card.find('p') or card.find(class_=re.compile(r'description|summary|excerpt|standfirst'))
            description = self.clean_text(desc_elem.get_text())[:500] if desc_elem else None
            
            # Get venue
            venue_elem = card.find(class_=re.compile(r'venue|location|address'))
            venue_name = self.clean_text(venue_elem.get_text()) if venue_elem else None
            
            # Get date
            date_elem = card.find('time') or card.find(class_=re.compile(r'date|when'))
            date_string = self.clean_text(date_elem.get_text()) if date_elem else None
            
            # Get image
            img_elem = card.find('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
            
            # Get category
            category_elem = card.find(class_=re.compile(r'category|tag|label'))
            category = self.clean_text(category_elem.get_text()) if category_elem else None
            
            if title and source_url:
                event = {
                    'title': title,
                    'date_string': date_string,
                    'date_time': self.parse_date(date_string) if date_string else None,
                    'venue_name': venue_name,
                    'venue_address': None,
                    'city': 'Sydney',
                    'description': description,
                    'category': category,
                    'tags': None,
                    'image_url': image_url,
                    'source_name': self.source_name,
                    'source_url': source_url,
                }
                event['content_hash'] = self.generate_content_hash(event)
                return event
                
        except Exception as e:
            logger.error(f"Error parsing Time Out card: {e}")
        
        return None

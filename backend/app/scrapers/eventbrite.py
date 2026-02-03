from typing import List, Dict, Any
from datetime import datetime
import re
import json
from app.scrapers.base import BaseScraper, logger


class EventbriteScraper(BaseScraper):
    """Scraper for Eventbrite Sydney events"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "Eventbrite"
        self.base_url = "https://www.eventbrite.com.au/d/australia--sydney/events/"
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Eventbrite"""
        events = []
        
        try:
            # Fetch the main events page
            html = await self.fetch_page(self.base_url)
            if not html:
                logger.warning("Failed to fetch Eventbrite page")
                return events
            
            soup = self.parse_html(html)
            
            # Find event cards - Eventbrite uses various class patterns
            event_cards = soup.find_all('div', {'data-testid': 'event-card'})
            
            # Also try alternative selectors
            if not event_cards:
                event_cards = soup.find_all('article', class_=re.compile(r'event-card'))
            
            if not event_cards:
                event_cards = soup.find_all('div', class_=re.compile(r'eds-event-card'))
            
            # Try to find embedded JSON data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Event':
                                event = self._parse_json_ld_event(item)
                                if event:
                                    events.append(event)
                    elif data.get('@type') == 'Event':
                        event = self._parse_json_ld_event(data)
                        if event:
                            events.append(event)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Parse HTML cards if JSON didn't work
            for card in event_cards[:30]:  # Limit to 30 events
                event = self._parse_event_card(card)
                if event and event.get('source_url') not in [e.get('source_url') for e in events]:
                    events.append(event)
            
            logger.info(f"Eventbrite: Scraped {len(events)} events")
            
        except Exception as e:
            logger.error(f"Eventbrite scraping error: {str(e)}")
        
        return events
    
    def _parse_json_ld_event(self, data: Dict) -> Dict[str, Any]:
        """Parse a JSON-LD event object"""
        try:
            location = data.get('location', {})
            address = location.get('address', {})
            
            # Handle address as string or object
            if isinstance(address, str):
                venue_address = address
            else:
                venue_address = ', '.join(filter(None, [
                    address.get('streetAddress', ''),
                    address.get('addressLocality', ''),
                    address.get('addressRegion', ''),
                    address.get('postalCode', '')
                ]))
            
            event = {
                'title': self.clean_text(data.get('name', '')),
                'date_string': data.get('startDate', ''),
                'date_time': self.parse_date(data.get('startDate', '')),
                'venue_name': self.clean_text(location.get('name', '')),
                'venue_address': self.clean_text(venue_address),
                'city': 'Sydney',
                'description': self.clean_text(data.get('description', ''))[:500] if data.get('description') else None,
                'category': None,
                'tags': None,
                'image_url': data.get('image', ''),
                'source_name': self.source_name,
                'source_url': data.get('url', ''),
            }
            
            if event['title'] and event['source_url']:
                event['content_hash'] = self.generate_content_hash(event)
                return event
                
        except Exception as e:
            logger.error(f"Error parsing JSON-LD event: {e}")
        
        return None
    
    def _parse_event_card(self, card) -> Dict[str, Any]:
        """Parse an event card HTML element"""
        try:
            # Try different selectors for title
            title_elem = card.find('h2') or card.find('h3') or card.find(class_=re.compile(r'event-card__title'))
            title = self.clean_text(title_elem.get_text()) if title_elem else None
            
            # Get link
            link_elem = card.find('a', href=True)
            source_url = link_elem['href'] if link_elem else None
            if source_url and not source_url.startswith('http'):
                source_url = f"https://www.eventbrite.com.au{source_url}"
            
            # Get date
            date_elem = card.find('p', class_=re.compile(r'date')) or card.find(class_=re.compile(r'event-card__date'))
            date_string = self.clean_text(date_elem.get_text()) if date_elem else None
            
            # Get venue
            venue_elem = card.find(class_=re.compile(r'location|venue'))
            venue_name = self.clean_text(venue_elem.get_text()) if venue_elem else None
            
            # Get image
            img_elem = card.find('img', src=True)
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            
            if title and source_url:
                event = {
                    'title': title,
                    'date_string': date_string,
                    'date_time': self.parse_date(date_string) if date_string else None,
                    'venue_name': venue_name,
                    'venue_address': None,
                    'city': 'Sydney',
                    'description': None,
                    'category': None,
                    'tags': None,
                    'image_url': image_url,
                    'source_name': self.source_name,
                    'source_url': source_url,
                }
                event['content_hash'] = self.generate_content_hash(event)
                return event
                
        except Exception as e:
            logger.error(f"Error parsing Eventbrite card: {e}")
        
        return None

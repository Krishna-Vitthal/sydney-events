from typing import List, Dict, Any
from datetime import datetime
import re
import json
from app.scrapers.base import BaseScraper, logger


class MeetupScraper(BaseScraper):
    """Scraper for Meetup Sydney events"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "Meetup"
        self.base_url = "https://www.meetup.com/find/?location=au--sydney&source=EVENTS"
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Meetup"""
        events = []
        
        try:
            html = await self.fetch_page(self.base_url)
            if not html:
                logger.warning("Failed to fetch Meetup page")
                return events
            
            soup = self.parse_html(html)
            
            # Look for Next.js data
            next_data = soup.find('script', id='__NEXT_DATA__')
            if next_data:
                try:
                    data = json.loads(next_data.string)
                    # Navigate through Next.js data structure
                    props = data.get('props', {}).get('pageProps', {})
                    results = props.get('searchResults', {}).get('edges', [])
                    
                    for edge in results[:30]:
                        node = edge.get('node', {})
                        event = self._parse_meetup_event(node)
                        if event:
                            events.append(event)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error parsing Meetup JSON data: {e}")
            
            # Fallback to HTML parsing
            if not events:
                event_cards = soup.find_all('div', {'data-testid': 'categoryResults-eventCard'})
                if not event_cards:
                    event_cards = soup.find_all('a', class_=re.compile(r'eventCard'))
                
                for card in event_cards[:30]:
                    event = self._parse_event_card(card)
                    if event:
                        events.append(event)
            
            logger.info(f"Meetup: Scraped {len(events)} events")
            
        except Exception as e:
            logger.error(f"Meetup scraping error: {str(e)}")
        
        return events
    
    def _parse_meetup_event(self, node: Dict) -> Dict[str, Any]:
        """Parse a Meetup event from API/Next.js data"""
        try:
            event_type = node.get('eventType')
            if event_type == 'PHYSICAL':
                venue = node.get('venue', {}) or {}
            else:
                venue = {}
            
            image = node.get('images', [{}])[0] if node.get('images') else {}
            
            date_time = None
            date_string = node.get('dateTime', '')
            if date_string:
                date_time = self.parse_date(date_string)
            
            event = {
                'title': self.clean_text(node.get('title', '')),
                'date_string': date_string,
                'date_time': date_time,
                'venue_name': self.clean_text(venue.get('name', '')),
                'venue_address': self.clean_text(venue.get('address', '')),
                'city': 'Sydney',
                'description': self.clean_text(node.get('description', ''))[:500] if node.get('description') else None,
                'category': node.get('group', {}).get('name', ''),
                'tags': None,
                'image_url': image.get('baseUrl', ''),
                'source_name': self.source_name,
                'source_url': node.get('eventUrl', ''),
            }
            
            if event['title'] and event['source_url']:
                event['content_hash'] = self.generate_content_hash(event)
                return event
                
        except Exception as e:
            logger.error(f"Error parsing Meetup event: {e}")
        
        return None
    
    def _parse_event_card(self, card) -> Dict[str, Any]:
        """Parse an event card HTML element"""
        try:
            # Get title
            title_elem = card.find('h2') or card.find('h3') or card.find(class_=re.compile(r'title'))
            title = self.clean_text(title_elem.get_text()) if title_elem else None
            
            # Get link
            if card.name == 'a':
                source_url = card.get('href', '')
            else:
                link_elem = card.find('a', href=True)
                source_url = link_elem['href'] if link_elem else None
            
            if source_url and not source_url.startswith('http'):
                source_url = f"https://www.meetup.com{source_url}"
            
            # Get date/time
            time_elem = card.find('time') or card.find(class_=re.compile(r'date|time'))
            date_string = self.clean_text(time_elem.get_text()) if time_elem else None
            
            # Get venue/location
            location_elem = card.find(class_=re.compile(r'location|venue|address'))
            venue_name = self.clean_text(location_elem.get_text()) if location_elem else None
            
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
            logger.error(f"Error parsing Meetup card: {e}")
        
        return None

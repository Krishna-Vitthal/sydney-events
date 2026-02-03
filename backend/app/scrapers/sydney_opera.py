from typing import List, Dict, Any
from datetime import datetime
import re
import json
from app.scrapers.base import BaseScraper, logger


class SydneyOperaHouseScraper(BaseScraper):
    """Scraper for Sydney Opera House events"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "Sydney Opera House"
        self.base_url = "https://www.sydneyoperahouse.com/whats-on"
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Sydney Opera House"""
        events = []
        
        try:
            html = await self.fetch_page(self.base_url)
            if not html:
                logger.warning("Failed to fetch Sydney Opera House page")
                return events
            
            soup = self.parse_html(html)
            
            # Look for JSON-LD structured data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') in ['Event', 'MusicEvent', 'TheaterEvent']:
                                event = self._parse_json_ld_event(item)
                                if event:
                                    events.append(event)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Find event cards
            event_cards = soup.find_all('article', class_=re.compile(r'event|show|performance'))
            if not event_cards:
                event_cards = soup.find_all('div', class_=re.compile(r'event-card|show-card'))
            if not event_cards:
                event_cards = soup.find_all('a', class_=re.compile(r'event|show'))
            
            for card in event_cards[:30]:
                event = self._parse_event_card(card)
                if event and event.get('source_url') not in [e.get('source_url') for e in events]:
                    events.append(event)
            
            logger.info(f"Sydney Opera House: Scraped {len(events)} events")
            
        except Exception as e:
            logger.error(f"Sydney Opera House scraping error: {str(e)}")
        
        return events
    
    def _parse_json_ld_event(self, data: Dict) -> Dict[str, Any]:
        """Parse a JSON-LD event object"""
        try:
            location = data.get('location', {})
            if isinstance(location, list):
                location = location[0] if location else {}
            
            address = location.get('address', {})
            if isinstance(address, str):
                venue_address = address
            else:
                venue_address = address.get('streetAddress', '')
            
            # Get image
            image = data.get('image', '')
            if isinstance(image, list):
                image = image[0] if image else ''
            if isinstance(image, dict):
                image = image.get('url', '')
            
            event = {
                'title': self.clean_text(data.get('name', '')),
                'date_string': data.get('startDate', ''),
                'date_time': self.parse_date(data.get('startDate', '')),
                'venue_name': 'Sydney Opera House',
                'venue_address': self.clean_text(venue_address) or 'Bennelong Point, Sydney NSW 2000',
                'city': 'Sydney',
                'description': self.clean_text(data.get('description', ''))[:500] if data.get('description') else None,
                'category': data.get('@type', '').replace('Event', ''),
                'tags': None,
                'image_url': image,
                'source_name': self.source_name,
                'source_url': data.get('url', ''),
            }
            
            if event['title'] and event['source_url']:
                event['content_hash'] = self.generate_content_hash(event)
                return event
                
        except Exception as e:
            logger.error(f"Error parsing Sydney Opera House JSON-LD: {e}")
        
        return None
    
    def _parse_event_card(self, card) -> Dict[str, Any]:
        """Parse an event card HTML element"""
        try:
            # Get title
            title_elem = card.find('h2') or card.find('h3') or card.find('h4') or card.find(class_=re.compile(r'title|heading'))
            title = self.clean_text(title_elem.get_text()) if title_elem else None
            
            # Get link
            if card.name == 'a':
                source_url = card.get('href', '')
            else:
                link_elem = card.find('a', href=True)
                source_url = link_elem['href'] if link_elem else None
            
            if source_url and not source_url.startswith('http'):
                source_url = f"https://www.sydneyoperahouse.com{source_url}"
            
            # Get date
            date_elem = card.find('time') or card.find(class_=re.compile(r'date|when'))
            date_string = self.clean_text(date_elem.get_text()) if date_elem else None
            
            # Get description
            desc_elem = card.find('p') or card.find(class_=re.compile(r'description|summary|excerpt'))
            description = self.clean_text(desc_elem.get_text())[:500] if desc_elem else None
            
            # Get image
            img_elem = card.find('img', src=True)
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            if image_url and not image_url.startswith('http'):
                image_url = f"https://www.sydneyoperahouse.com{image_url}"
            
            # Get category
            category_elem = card.find(class_=re.compile(r'category|genre|type'))
            category = self.clean_text(category_elem.get_text()) if category_elem else None
            
            if title and source_url:
                event = {
                    'title': title,
                    'date_string': date_string,
                    'date_time': self.parse_date(date_string) if date_string else None,
                    'venue_name': 'Sydney Opera House',
                    'venue_address': 'Bennelong Point, Sydney NSW 2000',
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
            logger.error(f"Error parsing Sydney Opera House card: {e}")
        
        return None

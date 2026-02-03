from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class EventStatus(str, enum.Enum):
    NEW = "new"
    UPDATED = "updated"
    INACTIVE = "inactive"
    IMPORTED = "imported"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    picture = Column(String(500))
    google_id = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    imports = relationship("EventImport", back_populates="user")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    date_time = Column(DateTime, index=True)
    date_string = Column(String(255))  # Original date string from source
    venue_name = Column(String(255))
    venue_address = Column(String(500))
    city = Column(String(100), default="Sydney", index=True)
    description = Column(Text)
    category = Column(String(255))
    tags = Column(String(500))  # Comma-separated
    image_url = Column(String(1000))
    source_name = Column(String(100), index=True)
    source_url = Column(String(1000), unique=True, index=True)
    
    # Status tracking
    status = Column(String(50), default=EventStatus.NEW.value, index=True)
    last_scraped_at = Column(DateTime, default=datetime.utcnow)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String(64))  # For detecting changes
    
    # Import tracking
    is_imported = Column(Boolean, default=False)
    imported_at = Column(DateTime)
    imported_by_id = Column(Integer, ForeignKey("users.id"))
    import_notes = Column(Text)
    
    ticket_leads = relationship("TicketLead", back_populates="event")
    import_record = relationship("EventImport", back_populates="event", uselist=False)


class TicketLead(Base):
    __tablename__ = "ticket_leads"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    consent = Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    event = relationship("Event", back_populates="ticket_leads")


class EventImport(Base):
    __tablename__ = "event_imports"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    imported_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    event = relationship("Event", back_populates="import_record")
    user = relationship("User", back_populates="imports")


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    events_found = Column(Integer, default=0)
    events_new = Column(Integer, default=0)
    events_updated = Column(Integer, default=0)
    events_inactive = Column(Integer, default=0)
    status = Column(String(50), default="running")
    error_message = Column(Text)

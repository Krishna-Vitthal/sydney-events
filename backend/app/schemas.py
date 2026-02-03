from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models import EventStatus


# User schemas
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    google_id: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Event schemas
class EventBase(BaseModel):
    title: str
    date_time: Optional[datetime] = None
    date_string: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    city: str = "Sydney"
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    source_name: str
    source_url: str


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: int
    status: str
    last_scraped_at: datetime
    first_seen_at: datetime
    is_imported: bool
    imported_at: Optional[datetime] = None
    imported_by_id: Optional[int] = None
    import_notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Ticket Lead schemas
class TicketLeadCreate(BaseModel):
    email: EmailStr
    consent: bool
    event_id: int


class TicketLeadResponse(BaseModel):
    id: int
    email: str
    consent: bool
    event_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Import schemas
class EventImportCreate(BaseModel):
    event_id: int
    notes: Optional[str] = None


class EventImportResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    imported_at: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# Dashboard filter schemas
class EventFilter(BaseModel):
    city: Optional[str] = "Sydney"
    keyword: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    source: Optional[str] = None
    page: int = 1
    per_page: int = 20


# Stats schema
class DashboardStats(BaseModel):
    total_events: int
    new_events: int
    updated_events: int
    inactive_events: int
    imported_events: int
    total_leads: int
    sources: List[str]

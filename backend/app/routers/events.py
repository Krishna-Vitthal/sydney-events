from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models import Event, TicketLead, EventImport, EventStatus, User
from app.schemas import (
    EventResponse, EventListResponse, TicketLeadCreate, 
    TicketLeadResponse, EventImportCreate, EventImportResponse,
    DashboardStats
)
from app.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=EventListResponse)
async def get_events(
    city: Optional[str] = Query(default="Sydney"),
    keyword: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    status: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of events with filters"""
    
    # Build query
    query = select(Event)
    count_query = select(func.count(Event.id))
    
    conditions = []
    
    # Filter by city
    if city:
        conditions.append(Event.city.ilike(f"%{city}%"))
    
    # Filter by keyword
    if keyword:
        keyword_condition = or_(
            Event.title.ilike(f"%{keyword}%"),
            Event.description.ilike(f"%{keyword}%"),
            Event.venue_name.ilike(f"%{keyword}%")
        )
        conditions.append(keyword_condition)
    
    # Filter by date range
    if date_from:
        conditions.append(Event.date_time >= date_from)
    if date_to:
        conditions.append(Event.date_time <= date_to)
    
    # Filter by status
    if status:
        conditions.append(Event.status == status)
    
    # Filter by source
    if source:
        conditions.append(Event.source_name == source)
    
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Get events
    query = query.order_by(Event.date_time.asc().nullsfirst()).offset(offset).limit(per_page)
    result = await db.execute(query)
    events = result.scalars().all()
    
    return EventListResponse(
        events=[EventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/sources")
async def get_event_sources(db: AsyncSession = Depends(get_db)):
    """Get list of unique event sources"""
    result = await db.execute(
        select(Event.source_name).distinct()
    )
    sources = [row[0] for row in result.fetchall()]
    return {"sources": sources}


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics (requires authentication)"""
    
    # Total events
    total_result = await db.execute(select(func.count(Event.id)))
    total_events = total_result.scalar()
    
    # Events by status
    status_counts = {}
    for status_val in [EventStatus.NEW, EventStatus.UPDATED, EventStatus.INACTIVE, EventStatus.IMPORTED]:
        result = await db.execute(
            select(func.count(Event.id)).where(Event.status == status_val.value)
        )
        status_counts[status_val.value] = result.scalar()
    
    # Also count imported events
    imported_result = await db.execute(
        select(func.count(Event.id)).where(Event.is_imported == True)
    )
    imported_count = imported_result.scalar()
    
    # Total leads
    leads_result = await db.execute(select(func.count(TicketLead.id)))
    total_leads = leads_result.scalar()
    
    # Get sources
    sources_result = await db.execute(select(Event.source_name).distinct())
    sources = [row[0] for row in sources_result.fetchall()]
    
    return DashboardStats(
        total_events=total_events,
        new_events=status_counts.get('new', 0),
        updated_events=status_counts.get('updated', 0),
        inactive_events=status_counts.get('inactive', 0),
        imported_events=imported_count,
        total_leads=total_leads,
        sources=sources
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single event by ID"""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return EventResponse.model_validate(event)


@router.post("/ticket-lead", response_model=TicketLeadResponse)
async def create_ticket_lead(
    lead: TicketLeadCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Create a ticket lead (user submits email for event)"""
    
    # Verify event exists
    result = await db.execute(select(Event).where(Event.id == lead.event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Create lead
    ticket_lead = TicketLead(
        email=lead.email,
        consent=lead.consent,
        event_id=lead.event_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(ticket_lead)
    await db.commit()
    await db.refresh(ticket_lead)
    
    return TicketLeadResponse.model_validate(ticket_lead)


@router.post("/{event_id}/import", response_model=EventImportResponse)
async def import_event(
    event_id: int,
    import_data: EventImportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import an event to the platform (requires authentication)"""
    
    # Verify event exists
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if already imported
    if event.is_imported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is already imported"
        )
    
    # Create import record
    event_import = EventImport(
        event_id=event_id,
        user_id=current_user.id,
        notes=import_data.notes
    )
    
    # Update event
    event.is_imported = True
    event.imported_at = datetime.utcnow()
    event.imported_by_id = current_user.id
    event.import_notes = import_data.notes
    event.status = EventStatus.IMPORTED.value
    
    db.add(event_import)
    await db.commit()
    await db.refresh(event_import)
    
    return EventImportResponse.model_validate(event_import)


@router.delete("/{event_id}/import")
async def unimport_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove import status from an event (requires authentication)"""
    
    # Verify event exists
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Remove import record
    import_result = await db.execute(
        select(EventImport).where(EventImport.event_id == event_id)
    )
    event_import = import_result.scalar_one_or_none()
    
    if event_import:
        await db.delete(event_import)
    
    # Update event
    event.is_imported = False
    event.imported_at = None
    event.imported_by_id = None
    event.import_notes = None
    event.status = EventStatus.UPDATED.value
    
    await db.commit()
    
    return {"message": "Event import removed"}

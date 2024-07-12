import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.models import schemas, ticket
from src.models.database import get_db
from src.models.schemas import TicketStatus, TicketCategory, TicketPriority, PaginatedTickets
from src.models.ticket import Ticket

router = APIRouter(prefix="/v1")


@router.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}


@router.post("/ticket", response_model=schemas.TicketResponse, status_code=201)
def create_ticket(data: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = ticket.Ticket(
        id=uuid.uuid4(),
        subject=data.subject,
        body=data.body,
        customer_email=data.customer_email,
        status=TicketStatus.SUBMITTED
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return {
        "ticket_id": db_ticket.id,
        "status": "submitted",
        "message": "Ticket submitted successfully and queued for processing"
    }


@router.get("/ticket/{ticket_id}", response_model=schemas.Ticket)
def get_ticket(ticket_id: uuid.UUID, db: Session = Depends(get_db)):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket %s not found" % ticket_id)
    return db_ticket


@router.get("/tickets", response_model=PaginatedTickets)
def get_tickets(status: Optional[TicketStatus] = None,
                category: Optional[TicketCategory] = None,
                priority: Optional[TicketPriority] = None,
                db: Session = Depends(get_db),
                page: int = Query(1, ge=1),  # Default page is 1, must be >= 1
                per_page: int = Query(50, gt=0, le=50)  # Default per_page is 50, max is 50
                ):
    """
    Filter tickets by status, category, and priority with pagination support.
    """
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    if priority:
        query = query.filter(Ticket.priority == priority)

    # Calculate the offset
    offset = (page - 1) * per_page

    # Apply limit and offset for pagination
    tickets = query.offset(offset).limit(per_page).all()

    return {
        "tickets": tickets,
        "total": len(tickets),
        "page": page,
        "per_page": per_page
    }

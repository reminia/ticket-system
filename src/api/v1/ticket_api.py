import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.worker import enqueue_tickets, enqueue_ticket
from src.models import schemas, ticket
from src.models.database import get_db
from src.models.schemas import TicketStatus, TicketCategory, TicketPriority, PaginatedTickets, TicketProcess
from src.models.ticket import Ticket

router = APIRouter(prefix="/v1")


@router.get("/ping")
def ping():
    """
    /v1 api liveness check
    """
    return {"status": "ok", "message": "pong"}


@router.post("/ticket", response_model=schemas.TicketCreateResponse, status_code=201)
def create_ticket(data: schemas.TicketCreate, db: Session = Depends(get_db)):
    """
    Create a ticket given ticket subject, body and customer email.

    Parameters:
    - **request body**: The data required to create a ticket, which includes:
      - **subject** (str): The subject of the ticket.
      - **body** (str): The body/content of the ticket.
      - **customer_email** (str): The email address of the customer creating the ticket.

    Returns:
    - **ticket_id**: uuid of the ticket.
    - **status**: Ticket status(submitted by default).
    - **message**: Ticket submitted successfully and queued for processing.

    Status Code:
    - **201**: Ticket created successfully.
    """
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
    enqueue_ticket(db_ticket.id)
    return {
        "ticket_id": db_ticket.id,
        "status": "submitted",
        "message": "Ticket submitted successfully and queued for processing"
    }


@router.get("/ticket/{ticket_id}", response_model=schemas.Ticket)
def get_ticket(ticket_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Query ticket by ticket id.

    Parameters:
    - **ticket_id**: The ticket id(uuid).

    Returns:
    - All fields of the ticket.
    """
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

    Parameters:
    - **status**: Filter by ticket status (submitted, processing, processed).
    - **category**: Filter by ticket category(Account Access, Feature Request, Unknown).
    - **priority**: Filter by ticket priority(Low, High).
    - **page**: Page number for pagination (default is 1).
    - **per_page**: Number of items per page for pagination (default is 50, max is 50).

    Returns:
    - **total**: Total number of tickets.
    - **page**: Current page number.
    - **per_page**: Number of tickets per page.
    - **tickets**: List of tickets.
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


@router.post("/process", response_model=TicketProcess)
def process_tickets(db: Session = Depends(get_db)):
    """manually trigger process of all unprocessed tickets"""
    unprocessed_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.SUBMITTED).all()
    if not unprocessed_tickets:
        return TicketProcess(message="No tickets to process", job_id="")

    tickets = [ticket.id for ticket in unprocessed_tickets]
    job = enqueue_tickets(tickets)
    return TicketProcess(
        message=f"Processing started for {len(unprocessed_tickets)} tickets",
        job_id=job.id
    )

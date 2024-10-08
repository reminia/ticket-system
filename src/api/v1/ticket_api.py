import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.worker import enqueue_tickets, enqueue_ticket
from src.models import schemas, ticket
from src.models.database import get_db
from src.models.schemas import TicketCreateResponse, PaginatedTickets, TicketProcess
from src.models.schemas import TicketStatus, TicketCategory, TicketPriority
from src.models.ticket import save_ticket, get_ticket as query_ticket
from src.models.ticket import filter_ticket, filter_ticket_status

router = APIRouter(prefix="/v1")


@router.post("/ticket", response_model=TicketCreateResponse, status_code=201)
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
    save_ticket(db, db_ticket)
    enqueue_ticket(db_ticket.id)
    return TicketCreateResponse(ticket_id=db_ticket.id,
                                status=TicketStatus.SUBMITTED.value,
                                message="Ticket submitted successfully and queued for processing")


@router.get("/ticket/{ticket_id}", response_model=schemas.Ticket)
def get_ticket(ticket_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Query ticket by ticket id.

    Parameters:
    - **ticket_id**: The ticket id(uuid).

    Returns:
    - All fields of the ticket.
    """
    db_ticket = query_ticket(db, ticket_id)
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
    tickets = filter_ticket(db, page, per_page, status, category, priority)
    return PaginatedTickets(tickets=tickets,
                            total=len(tickets),
                            page=page,
                            per_page=per_page)


@router.post("/process", response_model=TicketProcess)
def process_tickets(db: Session = Depends(get_db)):
    """Manually trigger process of all unprocessed tickets"""
    unprocessed_tickets = filter_ticket_status(db, TicketStatus.SUBMITTED)
    if not unprocessed_tickets:
        raise HTTPException(status_code=404, detail="No tickets remain to be processed")

    tickets = [ticket.id for ticket in unprocessed_tickets]
    job = enqueue_tickets(tickets)
    return TicketProcess(message=f"Processing started for {len(unprocessed_tickets)} tickets",
                         job_id=job.id)

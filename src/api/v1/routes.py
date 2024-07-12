import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models import schemas, ticket
from src.models.database import get_db
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
        status="submitted"
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
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket


# todo: page support
@router.get("/tickets", response_model=List[schemas.Ticket])
def get_tickets(status: Optional[str] = None,
                category: Optional[str] = None,
                priority: Optional[str] = None,
                db: Session = Depends(get_db)):
    """
    filter tickets by status, category and priority
    """
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    if priority:
        query = query.filter(Ticket.priority == priority)
    return query.all()

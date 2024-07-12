import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.models import schemas, ticket
from src.models.database import get_db

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

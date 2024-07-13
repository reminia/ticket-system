import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from .database import Base
from .schemas import TicketStatus, TicketCategory, TicketPriority


class Ticket(Base):
    """tickets table definition"""
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String, index=True)
    body = Column(String)
    customer_email = Column(String)
    status = Column(Enum(TicketStatus), default=TicketStatus.SUBMITTED)
    category = Column(Enum(TicketCategory), nullable=True)
    priority = Column(Enum(TicketPriority), nullable=True)
    initial_response = Column(String, nullable=True)
    category_confidence = Column(Float(precision=2), nullable=True)
    priority_confidence = Column(Float(precision=2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


def save_ticket(db: Session, ticket: Ticket):
    db.add(ticket)
    db.commit()
    db.refresh(ticket)


def get_ticket(db: Session, ticket_id: UUID) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def filter_ticket(db: Session,
                  page: int,
                  per_page: int,
                  status: Optional[TicketStatus] = None,
                  category: Optional[TicketCategory] = None,
                  priority: Optional[TicketPriority] = None
                  ) -> List[Ticket]:
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
    return query.offset(offset).limit(per_page).all()


def filter_ticket_status(db: Session, status: Optional[TicketStatus]) -> List[Ticket]:
    return db.query(Ticket).filter(Ticket.status == status).all()

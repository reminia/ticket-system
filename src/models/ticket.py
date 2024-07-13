import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import UUID

from .database import Base
from .schemas import TicketStatus, TicketCategory, TicketPriority


class Ticket(Base):
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

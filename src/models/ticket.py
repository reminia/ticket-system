from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from datetime import datetime
import uuid


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String, index=True)
    body = Column(String)
    customer_email = Column(String)
    status = Column(String, default="submitted")
    category = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    initial_response = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

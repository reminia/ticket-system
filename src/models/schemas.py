from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4, ConfigDict


class TicketBase(BaseModel):
    subject: str
    body: str
    customer_email: EmailStr


class TicketCreate(TicketBase):
    pass


class TicketResponse(BaseModel):
    ticket_id: UUID4
    status: str
    message: str


class TicketStatus(Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    PROCESSED = "processed"


class TicketPriority(Enum):
    LOW = "Low"
    HIGH = "High"


class TicketCategory(Enum):
    ACCOUNT_ACCESS = "Account Access"
    FEATURE_REQUEST = "Feature Request"
    UNKNOWN = "Unknown"


class Ticket(TicketBase):
    id: UUID4
    status: Optional[TicketStatus]
    category: Optional[TicketCategory]
    priority: Optional[TicketPriority]
    initial_response: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

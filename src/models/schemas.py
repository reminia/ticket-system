from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, UUID4, ConfigDict


class TicketBase(BaseModel):
    subject: str
    body: str
    customer_email: EmailStr


class TicketCreate(TicketBase):
    pass


class TicketCreateResponse(BaseModel):
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
    category_confidence: Optional[float]
    priority_confidence: Optional[float]
    created_at: datetime
    processed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PaginatedTickets(BaseModel):
    tickets: List[Ticket]
    total: int
    page: int
    per_page: int


class TicketProcess(BaseModel):
    message: str
    job_id: UUID4


class TicketClassified(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    category_confidence: float
    priority_confidence: float

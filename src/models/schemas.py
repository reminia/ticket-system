from pydantic import BaseModel, EmailStr, UUID4, ConfigDict
from datetime import datetime
from typing import Optional


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


class Ticket(TicketBase):
    id: UUID4
    status: str
    category: Optional[str]
    priority: Optional[str]
    initial_response: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

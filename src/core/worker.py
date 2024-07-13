import logging
from typing import List
from uuid import UUID

from redis import Redis
from rq import Queue
from rq.job import Job
from sqlalchemy.exc import SQLAlchemyError

from src.core.ai import categorize_prioritize_ticket
from src.core.config import settings
from src.models.database import get_db
from src.models.schemas import TicketStatus
from src.models.ticket import get_ticket

redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue(connection=redis_conn)
logger = logging.getLogger(__name__)


def process_ticket(ticket_id: UUID):
    logger.info(f"Processing ticket with id: {ticket_id}")
    db = get_db()
    try:
        ticket = get_ticket(db, ticket_id)
        ticket.status = TicketStatus.PROCESSING
        db.commit()
        db.refresh(ticket)
        logger.info(f"Set ticket {ticket_id} status to PROCESSING")
        ticket_classified = categorize_prioritize_ticket(ticket)
        ticket.category = ticket_classified.category
        ticket.category_confidence = ticket_classified.category_confidence
        ticket.priority = ticket_classified.priority
        ticket.priority_confidence = ticket_classified.priority_confidence
        db.commit()
        logger.info(f"Process ticket {ticket_id} done")
    except SQLAlchemyError as e:
        logger.error(f"Database error while processing ticket {ticket_id}: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error while processing ticket {ticket_id}: {e}")
        raise


def process_tickets(tickets: List[UUID]):
    for ticket in tickets:
        process_ticket(ticket)


def enqueue_ticket(ticket_id: UUID) -> Job:
    return queue.enqueue(process_ticket, ticket_id)


def enqueue_tickets(tickets: List[UUID]) -> Job:
    return queue.enqueue(process_tickets, tickets)

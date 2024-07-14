import asyncio
from datetime import datetime
from typing import List
from uuid import UUID

from redis import Redis
from rq import Queue
from rq.job import Job
from src.core.ai import categorize_prioritize_ticket, craft_ticket_response
from src.core.config import settings
from src.core.utils import setup_logger
from src.models.database import SessionLocal
from src.models.schemas import TicketStatus
from src.models.ticket import get_ticket

redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue(connection=redis_conn)
logger = setup_logger()


async def process_ticket(ticket_id: UUID):
    logger.info(f"Processing ticket {ticket_id}")
    db = SessionLocal()
    try:
        with db.begin():
            ticket = get_ticket(db, ticket_id)
            ticket.status = TicketStatus.PROCESSING
        logger.info(f"Set ticket {ticket_id} status to PROCESSING")

        with db.begin():
            classify_ticket = categorize_prioritize_ticket(ticket)
            respond_ticket = craft_ticket_response(ticket)
            ticket_classified, response = await asyncio.gather(classify_ticket, respond_ticket)
            ticket.category = ticket_classified.category
            ticket.category_confidence = ticket_classified.category_confidence
            ticket.priority = ticket_classified.priority
            ticket.priority_confidence = ticket_classified.priority_confidence
            ticket.processed_at = datetime.utcnow()
            ticket.initial_response = response
            ticket.status = TicketStatus.PROCESSED

        logger.info(f"Process ticket {ticket_id} done")

    except Exception as e:
        try:
            # revert ticket status
            with db.begin():
                ticket.status = TicketStatus.SUBMITTED
            logger.info(f"Revert ticket {ticket_id} to submitted status")
        except Exception as e:
            logger.error(f"Failed to revert ticket {ticket_id} to submitted status: {e}")
            raise
        logger.error(f"Unexpected error while processing ticket {ticket_id}: {e}")
        raise
    finally:
        db.close()


def process_ticket_job(ticket_id: UUID):
    asyncio.run(process_ticket(ticket_id))


def enqueue_ticket(ticket_id: UUID) -> Job:
    return queue.enqueue(process_ticket_job, ticket_id)


def process_tickets(tickets: List[UUID]):
    for ticket in tickets:
        enqueue_ticket(ticket)


def enqueue_tickets(tickets: List[UUID]) -> Job:
    return queue.enqueue(process_tickets, tickets)

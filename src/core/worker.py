from typing import List
from uuid import UUID

from redis import Redis
from rq import Queue
from rq.job import Job

from src.core.config import settings

redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue(connection=redis_conn)


# todo: update ticket status in db & process ticket with ai
def process_ticket(ticket_id: UUID):
    pass


def process_tickets(tickets: List[UUID]):
    for ticket in tickets:
        process_ticket(ticket)


def enqueue_ticket(ticket_id: UUID) -> Job:
    return queue.enqueue(process_ticket, ticket_id)


def enqueue_tickets(tickets: List[UUID]) -> Job:
    return queue.enqueue(process_tickets, tickets)

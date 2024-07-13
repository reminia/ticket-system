from rq import Queue
from redis import Redis
import anthropic
from src.models.database import SessionLocal
from src.models.ticket import Ticket
from datetime import datetime
from src.core.config import settings

redis_conn = Redis.from_url(settings.REDIS_URL)
q = Queue(connection=redis_conn)

client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)


def process_ticket(ticket_id: int):
    db = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if ticket and ticket.status == "unprocessed":
        prompt = f"Categorize the following support ticket:\nTitle: {ticket.title}\nDescription: {ticket.description}\n\nCategory:"
        response = client.completions.create(
            model="claude-3-opus-20240229",
            prompt=prompt,
            max_tokens_to_sample=100,
        )
        category = response.completion.strip()

        ticket.status = "processed"
        ticket.category = category
        ticket.processed_at = datetime.utcnow()
        db.commit()

    db.close()


def enqueue_ticket(ticket_id: int):
    q.enqueue(process_ticket, ticket_id)

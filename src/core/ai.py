import logging

import anthropic

from src.core.config import settings
from src.core.utils import enum2csv
from src.models.schemas import TicketClassified, TicketCategory, TicketPriority
from src.models.ticket import Ticket

claudAI = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
logger = logging.getLogger(__name__)


def categorize_prioritize_ticket(ticket: Ticket) -> TicketClassified:
    prompt = f"""
    Analyze the following ticket and categorize it into one of these categories: {enum2csv(TicketCategory, ", ")}
    Also, assign a priority among {enum2csv(TicketPriority, ", ")}
    Finally, provide a confidence level (0.0 to 1.0) for both the category and priority.

    Ticket Subject: {ticket.subject}
    Ticket Content: {ticket.body}

    Respond with a JSON object in the following format:
    {{
        "category": "Category name",
        "category_confidence": 0.0,
        "priority": "Priority level",
        "priority_confidence": 0.0
    }}
    
    Ensure the JSON is valid and contains only the specified fields.
    """
    logger.info("Classify ticket by claudAI")
    try:
        response = claudAI.completions.create(
            model="claude-3-opus-20240229",
            prompt=prompt,
            max_tokens_to_sample=200,
            temperature=0,
        )
        # todo: check claudAI response error
        return TicketClassified.parse_raw(response.completion.strip())
    except Exception as e:
        logging.error(f"classify ticket {ticket.id} failed: {e}")
        raise e


def initial_response_ticket():
    pass

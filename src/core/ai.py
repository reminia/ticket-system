import logging

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic

from src.core.config import settings
from src.core.utils import enum2csv
from src.models.schemas import TicketClassified, TicketCategory, TicketPriority
from src.models.ticket import Ticket

logger = logging.getLogger(__name__)

classify_prompt = PromptTemplate(
    input_variables=["ticket_subject", "ticket_body", "categories", "priorities"],
    template="""
    Analyze the following ticket and categorize it into one of these categories: {categories}
    Also, assign a priority among {priorities}
    Finally, provide a confidence level (0.0 to 1.0) for both the category and priority.

    Ticket Subject: {ticket_subject}
    Ticket Content: {ticket_body}

    Respond with a JSON object in the following format:
    {{
        "category": "Category name",
        "category_confidence": 0.0,
        "priority": "Priority level",
        "priority_confidence": 0.0
    }}
    
    Ensure the JSON is valid and contains only the specified fields.
    """
)

anthropic_llm = ChatAnthropic(model="claude-3-opus-20240229", api_key=settings.ANTHROPIC_API_KEY)
output_parser = PydanticOutputParser(pydantic_object=TicketClassified)
chain = classify_prompt | anthropic_llm | output_parser


def categorize_prioritize_ticket(ticket: Ticket) -> TicketClassified:
    logger.info("Classify ticket by LangChain")
    try:
        chain_input = {
            "ticket_subject": ticket.subject,
            "ticket_body": ticket.body,
            "categories": enum2csv(TicketCategory, ", "),
            "priorities": enum2csv(TicketPriority, ", ")
        }
        # Run the chain
        return chain.invoke(chain_input)
    except Exception as e:
        logger.error(f"Classify ticket {ticket.id} failed: {e}")
        raise e

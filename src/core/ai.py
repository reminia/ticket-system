from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.core.custom_anthropic import CustomChatAnthropic
from src.core.utils import enum2csv, setup_logger
from src.models.schemas import TicketClassified, TicketCategory, TicketPriority
from src.models.ticket import Ticket

logger = setup_logger(__name__)

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

anthropic_llm = CustomChatAnthropic(model=settings.ANTHROPIC_MODEL,
                                    api_key=settings.ANTHROPIC_API_KEY,
                                    base_url=settings.ANTHROPIC_PROXY_URL,
                                    max_tokens=100)
output_parser = PydanticOutputParser(pydantic_object=TicketClassified)
classify_chain = classify_prompt | anthropic_llm | output_parser

response_prompt = PromptTemplate(
    input_variables=["ticket_subject", "ticket_body"],
    template="""
    Craft an initial response to the following ticket.

    Ticket Subject: {ticket_subject}
    Ticket Content: {ticket_body}

    Respond only with a text containing the initial response to the customer.
    Don't add any ending words like 'best regards 'in the response.
    """
)
openai_llm = ChatOpenAI(model=settings.OPENAI_MODEL,
                        api_key=settings.OPENAI_API_KEY,
                        base_url=settings.OPENAI_PROXY_URL,
                        max_tokens=100)
response_chain = response_prompt | openai_llm | StrOutputParser()


async def categorize_prioritize_ticket(ticket: Ticket) -> TicketClassified:
    logger.info("Classify ticket by Anthropic llm")
    try:
        chain_input = {
            "ticket_subject": ticket.subject,
            "ticket_body": ticket.body,
            "categories": enum2csv(TicketCategory, ", "),
            "priorities": enum2csv(TicketPriority, ", ")
        }
        return await classify_chain.ainvoke(chain_input)
    except Exception as e:
        logger.error(f"Classify ticket {ticket.id} failed: {e}")
        raise e


async def craft_ticket_response(ticket: Ticket) -> str:
    logger.info("Response to ticket with OpenAI llm")
    try:
        chain_input = {
            "ticket_subject": ticket.subject,
            "ticket_body": ticket.body
        }
        return await response_chain.ainvoke(chain_input)
    except Exception as e:
        logger.error(f"Response to ticket {ticket.id} failed: {e}")
        raise e

import anthropic

from src.core.config import settings

client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)


def categorize_prioritize_ticket():
    pass


def initial_response_ticket():
    pass

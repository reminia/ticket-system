from src.core.utils import enum2csv
from src.models.schemas import TicketPriority


def test_enum2csv():
    assert enum2csv(TicketPriority) == "Low,High"

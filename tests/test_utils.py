import logging
from io import StringIO

from src.core.utils import enum2csv, setup_logger
from src.models.schemas import TicketPriority


def test_enum2csv():
    assert enum2csv(TicketPriority) == "Low,High"


def test_setup_logger():
    logger = setup_logger(__name__, logging.DEBUG)
    assert logger.level == logging.DEBUG

    stream = StringIO()
    logger.handlers[0].stream = stream  # Redirect output to our string buffer
    message = "log message"
    logger.info(message)

    log_output = stream.getvalue().strip()
    assert message in log_output
    # assert logger name
    assert __name__ in log_output

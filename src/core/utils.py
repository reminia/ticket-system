import logging
from enum import Enum
from typing import Type


def enum2csv(clazz: Type[Enum], sep: str = ',') -> str:
    words = [str(item.value) for item in clazz]
    return sep.join(words)


def setup_logger(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

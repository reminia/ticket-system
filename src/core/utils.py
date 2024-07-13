from enum import Enum
from typing import Type


def enum2csv(clazz: Type[Enum], sep: str = ',') -> str:
    words = [str(item.value) for item in clazz]
    return sep.join(words)

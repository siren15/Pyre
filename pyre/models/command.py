from typing import Any, List, Optional
from .base import PyreObject

class BaseCommand(PyreObject):
    name: str
    description: str
    aliases: Optional[List[str]] = []
    args: List[Any]
    callback: callable




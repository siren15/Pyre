from typing import Any, List, Optional
from .base import PyreObject
from pydantic import BaseModel

class CommandArg(BaseModel):
    name: str
    type: PyreObject|str|int|bool|list|Any

class BaseCommand(PyreObject):
    name: str = None
    subcommand: str = None
    description: str = "No description"
    aliases: Optional[List[str]] = []
    args: List[CommandArg] = []
    callback: callable

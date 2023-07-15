from typing import Optional
from pydantic import Field as field
from .base import PyreObject


class BaseEmoji(PyreObject):
    id: str = field(alias='_id')
    creator_id: str
    name: str
    animated: Optional[bool] = False
    nsfw: Optional[bool] = False


class ServerParent(PyreObject):
    type: str
    id: str


class DetachedParent(PyreObject):
    type: str


class ServerEmoji(BaseEmoji):
    parent: ServerParent = None


class DetachedEmoji(BaseEmoji):
    parent: DetachedParent = None

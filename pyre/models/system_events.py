from typing import Union
from pydantic import Field as field
from .base import SystemEvent


class Text(SystemEvent):
    content: str


class UserAdded(SystemEvent):
    id: str
    by: str


class UserRemoved(SystemEvent):
    id: str
    by: str


class UserJoined(SystemEvent):
    id: str


class UserLeft(SystemEvent):
    id: str


class UserKicked(SystemEvent):
    id: str


class UserBanned(SystemEvent):
    id: str


class ChannelRenamed(SystemEvent):
    name: str
    by: str


class ChannelDescriptionChanged(SystemEvent):
    by: str


class ChannelIconChanged(SystemEvent):
    by: str


class ChannelOwnershipChanged(SystemEvent):
    original: str
    to: str


SYS_EVENT_MSGS = Union[Text, UserAdded, UserRemoved, UserJoined, UserLeft,
                       UserKicked, UserBanned, ChannelRenamed,
                       ChannelDescriptionChanged, ChannelIconChanged,
                       ChannelOwnershipChanged]

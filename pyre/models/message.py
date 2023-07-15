from typing import Optional, Any, List, TYPE_CHECKING, Union
from datetime import datetime
from pydantic import Field as field, FilePath
from pydantic_extra_types import color
from .base import PyreObject
from .system_events import SYS_EVENT_MSGS
from .file import UPLOADABLE_TYPE, File
from .embed import EMBEDS, Embed

if TYPE_CHECKING:
    from .server import Server
    from .channel import TextChannel
    from .user import Member


class Reply(PyreObject):
    id: str
    mention: bool = False


class Masquerade(PyreObject):
    name: str = None
    avatar: str = None
    colour: Optional[color.Color] = color.Color('ff4655')


class Interactions(PyreObject):
    reactions: List[str] = None
    restrict_reactions: bool = False


class PartialWebhook(PyreObject):
    name: str
    avatar: str = None


class Webhook(PyreObject):
    id: str
    name: str
    channel_id: str
    avatar: File = None
    token: str = None


class PartialMessage(PyreObject):
    content: Optional[str] = None
    edited: Optional[datetime] = None
    embeds: Optional[List[EMBEDS]] = None


class TextMessage(PyreObject):
    id: str = field(alias='_id', default=None)
    channel_id: str = field(alias='channel', default=None)
    author_id: str = field(alias='author', default=None)
    nonce: Optional[str] = None
    webhook: Optional[PartialWebhook] = None
    content: Optional[str] = None
    system: Optional[SYS_EVENT_MSGS] = None
    attachments: Optional[List[File]] = None
    edited: Optional[datetime] = None
    embeds: Optional[List[EMBEDS]] = None
    mentions: Optional[List[str]] = None
    replies: Optional[List[str]] = None
    reactions: Optional[List[Any]] = None
    interactions: Optional[Interactions] = None
    masquerade: Masquerade = None

    @property
    def server(self) -> "Server":
        channel = self.client.cache.get_channel(self.channel_id)
        return channel.server

    @property
    def channel(self) -> "TextChannel":
        return self.client.cache.get_channel(self.channel_id)

    @property
    def author(self) -> "Member":
        return self.client.cache.get_member(self.server.id, self.author_id)
    
    async def reply(self,
                    content: str = None,
                    attachments: List[UPLOADABLE_TYPE] = [],
                    file: UPLOADABLE_TYPE = None,
                    embeds: List[Embed] = [],
                    embed: Embed = None,
                    masquerade: Masquerade = None,
                    interactions: Interactions = None,
                    spoiler_attachments: bool = False,
                    mention: bool = False):
        return await self.client.http.reply(self.channel_id, self.id, content, attachments, file, embeds, embed, masquerade, interactions, spoiler_attachments, mention)

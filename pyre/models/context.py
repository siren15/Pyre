from typing import List
from .user import Member
from .server import Server
from .channel import MESSAGEABLE
from .command import BaseCommand
from .base import PyreObject
from .message import Interactions, Masquerade, Reply, TextMessage
from .file import UPLOADABLE_TYPE, File
from .embed import EMBEDS, Embed


class BaseContext(PyreObject):
    server_id: str

class CommandContext(BaseContext):
    command: BaseCommand
    author_id: str
    channel_id: str
    message_id: str

    @property
    def server(self) -> Server:
        return self.client.cache.get_server(self.server_id)
    
    @property
    def author(self) -> Member:
        return self.server.get_member(self.author_id)
    
    @property
    def message(self) -> TextMessage:
        return self.client.cache.get_message(self.channel_id, self.message_id)
    
    @property
    def channel(self) -> MESSAGEABLE:
        return self.server.get_channel(self.channel_id)

    async def reply(self, content: str = None,
                    attachments: List[UPLOADABLE_TYPE] = [],
                    file: UPLOADABLE_TYPE = None,
                    embeds: List[Embed] = [],
                    embed: Embed = None,
                    masquerade: Masquerade = None,
                    interactions: Interactions = None,
                    spoiler_attachments: bool = False,
                    mention: bool = False) -> TextMessage:
        return await self.message.reply(
            content,
            attachments,
            file,
            embeds,
            embed,
            masquerade,
            interactions,
            spoiler_attachments,
            mention
        )
    
    async def send(self,
                   content: str = None,
                   file: UPLOADABLE_TYPE = None,
                   attachments: List[UPLOADABLE_TYPE] = [],
                   replies: List[Reply] = None,
                   embed: Embed = None,
                   embeds: List[Embed] = [],
                   masquerade: Masquerade = None,
                   interactions: Interactions = None,
                   spoiler_attachments: bool = False):
        return await self.channel.send(
            content,
            file,
            attachments,
            replies,
            embed,
            embeds,
            masquerade,
            interactions,
            spoiler_attachments
        )


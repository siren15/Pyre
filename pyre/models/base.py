from typing import TYPE_CHECKING, Dict, Any, List, ForwardRef
from pydantic import BaseModel, Field, FilePath, model_validator, ConfigDict

if TYPE_CHECKING:
    from pyre.client import PyreClient
    from .server import Server
    from .channel import TYPE_ALL_CHANNEL, TextChannel
    from .message import TextMessage, Reply, Masquerade, Interactions
    from .user import Member
    from .file import UPLOADABLE_TYPE
    from .embed import Embed

FUF = ForwardRef("UploadableFile")

def delete_key(dict_key:str, d: Dict):
    """Delete any instance of key from dictionary, and it's nested dictionaries"""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == dict_key:
                del d[key]
            elif isinstance(d[key], dict):
                delete_key(dict_key, d[key])
    return d

class PyreObject(BaseModel):
    """The base object meant to be used by all objects"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    wsclient: Any = Field(repr=False, default=None)
    """The bot client, used only for internal purposes"""
    
    @property
    def client(self) -> "PyreClient":
        """Return the bot client"""
        return self.wsclient

    @model_validator(mode='after')
    def validate(cls, data):
        if data.wsclient:
            client = data.wsclient
            for name, value in data:
                if hasattr(value, "wsclient"):
                    value.wsclient = client
        return data
    
    def to_dict(self) -> Dict:
        """Return the model as dict, without client"""
        return delete_key('wsclient', self.model_dump())
    

class SendableObject(PyreObject):
    """For objects that you can send stuff to."""

    async def send(self,
                   content: str = None,
                   file: UPLOADABLE_TYPE = None,
                   attachments: List[UPLOADABLE_TYPE] = [],
                   replies: List["Reply"] = None,
                   embed: "Embed" = None,
                   embeds: List["Embed"] = [],
                   masquerade: "Masquerade" = None,
                   interactions: "Interactions" = None,
                   spoiler_attachments: bool = False,
    ):
        if embed:
            embeds.append(embed)
        if file:
            attachments.append(file)
        return await self.client.http.send_message(channel_id=self.id,
                                                   content=content,
                                                   attachments=attachments,
                                                   embeds=embeds,
                                                   masquerade=masquerade,
                                                   interactions=interactions,
                                                   spoiler_attachments=spoiler_attachments,
                                                   replies=replies)


class PyreEvent(PyreObject):
    """The base event for all events"""


class ServerEvent(PyreEvent):
    """The base event for server events, not meant to be used by itself"""

    @property
    def server(self) -> "Server":
        """The server this event is part of"""
        return self.client.cache.get_server(self.server_id)


class ChanelEvent(SendableObject):
    """The base event for channel events, not meant to be used by itself"""

    @property
    def server(self) -> "Server":
        """The server this event is part of"""
        channel = self.client.cache.get_channel(self.channel_id)
        return channel.server

    @property
    def channel(self) -> "TYPE_ALL_CHANNEL":
        """The channel this event is part of"""
        return self.client.cache.get_channel(self.channel_id)


class MessageEvent(PyreEvent):
    """The base event for message events"""

    @property
    def server(self) -> "Server":
        return self.channel.server

    @property
    def channel(self) -> "TextChannel":
        return self.client.cache.get_channel(self.channel_id)

    @property
    def author(self) -> "Member":
        return self.client.cache.get_member(self.server.id, self.author_id)

    @property
    def message(self) -> "TextMessage":
        return self.client.cache.get_message(self.channel_id, self.message_id)
    
    async def reply(self, content: str = None, 
                    attachments: List[FUF | str] = None,
                    embeds: List["Embed"] = None,
                    masquerade: "Masquerade" = None,
                    interactions: "Interactions" = None,
                    spoiler_attachments: bool = False,
                    mention:bool=False):
        return await self.client.http.send_message(channel_id=self.channel_id,
                                                   content=content,
                                                   attachments=attachments,
                                                   embeds=embeds,
                                                   masquerade=masquerade,
                                                   interactions=interactions,
                                                   spoiler_attachments=spoiler_attachments,
                                                   replies=[Reply(id=self.id, mention=mention)])


class MemberEvent(PyreEvent):
    """The base for member events"""

    @property
    def member(self) -> "Member":
        if self.__name__ == 'ServerMemberLeave':
            return self.client.cache.get_deleted_member(self.server_id, self.user_id)
        return self.client.cache.get_member(self.server_id, self.user_id)

    @property
    def server(self) -> "Server":
        """The server this event is part of"""
        return self.client.cache.get_server(self.server_id)


class SystemEvent(PyreObject):
    """System messages base object"""
    type: str  # = 'text' | "user_added" | "user_remove" | "user_joined" | "user_left" | "user_kicked" | "user_banned" | "channel_renamed" | "channel_description_changed" | "channel_icon_changed" | "channel_ownership_changed"

from typing import Optional, Any, List, Union
from pydantic import Field as field, FilePath
from datetime import datetime
from .base import PyreEvent, PyreObject, ServerEvent, ChanelEvent, MessageEvent, MemberEvent
from .message import Interactions, Reply, Webhook, Masquerade, TextMessage
from .embed import Embed, EMBEDS
from .channel import TextChannel, TYPE_ALL_CHANNEL
from .server import Server
from .user import Member, MemberIds, User, RelationshipStatus
from .file import File, UPLOADABLE_TYPE
from .role import Role
from .emoji import ServerParent


class MessageCreate(PyreEvent):
    """Dispatched when a message is created"""
    event_type: str = field(alias='type', repr=False)
    id: str = field(alias='_id')
    channel_id: str = field(alias="channel")
    author_id: str = field(alias='author')
    nonce: Optional[str] = None
    webhook: Optional[Webhook] = None
    content: Optional[str] = None
    system: Optional[Any] = None
    attachments: Optional[List[File]] = None
    edited: Optional[datetime] = None
    embeds: Optional[List[EMBEDS]] = None
    mentions: Optional[List[str]] = None
    replies: Optional[List[str]] = None
    reactions: Optional[List[Any]] = None
    interactions: Optional[Interactions] = None
    masquerade: Masquerade = None

    @property
    def server(self) -> Server:
        return self.channel.server

    @property
    def channel(self) -> TextChannel:
        return self.client.cache.get_channel(self.channel_id)

    @property
    def author(self) -> Member:
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


class MessageUpdate(MessageEvent):
    """Dispatched when message is updated."""
    event_type: str = field(alias='type', repr=False)
    message_id: str = field(alias='id')
    channel_id: str = field(alias="channel")
    data: TextMessage = None

    @property
    def after(self) -> TextMessage:
        return self.client.cache.get_message(self.channel_id, self.message_id)

    @property
    def before(self) -> TextMessage:
        return self.client.cache.get_deleted_message(self.channel_id,
                                                     self.message_id)


class Append(PyreObject):
    embeds: Optional[List[EMBEDS]] = None


class MessageAppend(MessageEvent):
    event_type: str = field(alias='type', repr=False)
    message_id: str = field(alias='id')
    channel_id: str = field(alias="channel")
    append: Append


class MessageDelete(MessageEvent):
    """Dispatched when message is deleted"""
    event_type: str = field(alias='type', repr=False)
    message_id: str = field(alias='id')
    channel_id: str = field(alias="channel")

    @property
    def before(self) -> TextMessage:
        return self.client.cache.get_deleted_message(self.channel_id,
                                                     self.message_id)


class MessageReact(MessageEvent):
    event_type: str = field(alias='type', repr=False)
    message_id: str = field(alias='id')
    channel_id: str
    user_id: str
    emoji_id: str


class MessageUnreact(MessageEvent):
    event_type: str = field(alias='type', repr=False)
    message_id: str = field(alias='id')
    channel_id: str
    user_id: str
    emoji_id: str


class MessageRemoveReaction(MessageEvent):
    event_type: str = field(alias='type', repr=False)
    message_id: str = field(alias='id')
    channel_id: str
    emoji_id: str


class ChannelCreate(PyreEvent):
    channel: TYPE_ALL_CHANNEL


class ChannelUpdate(ChanelEvent):
    event_type: str = field(alias='type', repr=False)
    channel_id: str = field(alias='id')
    data: TYPE_ALL_CHANNEL = None
    clear: List[str] = None

    @property
    def before(self) -> TYPE_ALL_CHANNEL:
        return self.client.cache.deleted.get(self.channel_id)

    @property
    def after(self) -> TYPE_ALL_CHANNEL:
        return self.client.cache.get_channel(self.channel_id)


class ChannelDelete(ChanelEvent):
    event_type: str = field(alias='type', repr=False)
    channel_id: str = field(alias='id')


class ChannelGroupJoin(ChanelEvent):
    event_type: str = field(alias='type', repr=False)
    channel_id: str = field(alias='id')
    user_id: str = field(alias='user')


class ChannelGroupLeave(ChanelEvent):
    event_type: str = field(alias='type', repr=False)
    channel_id: str = field(alias='id')
    user_id: str = field(alias='user')


class ChannelStartTyping(ChanelEvent):
    event_type: str = field(alias='type', repr=False)
    channel_id: str = field(alias='id')
    user_id: str = field(alias='user')


class ChannelStopTyping(ChanelEvent):
    event_type: str = field(alias='type', repr=False)
    channel_id: str = field(alias='id')
    user_id: str = field(alias='user')


class ChannelAck(ChanelEvent):
    event_type: str = field(alias='type', repr=False)
    channel_id: str = field(alias='id')
    user_id: str = field(alias='user')
    message_id: str


class ServerCreate(PyreEvent):
    event_type: str = field(alias='type', repr=False)
    server_id: str = field(alias='id')
    server: Server
    channels: List[TYPE_ALL_CHANNEL] = None


class ServerUpdate(ServerEvent):
    event_type: str = field(alias='type', repr=False)
    server_id: str = field(alias='id')
    data: Server = None
    clear: List[str] = None


class ServerDelete(ServerEvent):
    event_type: str = field(alias='type', repr=False)
    server_id: str = field(alias='id')


class ServerMemberUpdate(PyreEvent):
    event_type: str = field(alias='type', repr=False)
    ids: MemberIds = field(alias='id')
    data: Member = None
    clear: Optional[List[str]] = None

    @property
    def before(self) -> Member:
        return self.client.cache.get_deleted_member(self.ids.server_id,
                                                    self.ids.user_id)

    @property
    def member(self) -> Member:
        return self.client.cache.get_member(self.ids.server_id,
                                            self.ids.user_id)

    @property
    def after(self) -> Member:
        return self.member

    @property
    def server(self) -> Server:
        return self.client.cache.get_serer(self.ids.server_id)


class ServerMemberJoin(MemberEvent):
    event_type: str = field(alias='type', repr=False)
    server_id: str = field(alias='id')
    user_id: str = field(alias='user')


class ServerMemberLeave(MemberEvent):
    event_type: str = field(alias='type', repr=False)
    server_id: str = field(alias='id')
    user_id: str = field(alias='user')


class ServerRoleUpdate(ServerEvent):
    event_type: str = field(alias='type', repr=False)
    server_id: str = field(alias='id')
    role_id: str
    data: Role = None
    clear: List[str] = None

    @property
    def before(self):
        return self.client.cache.get_deleted_role(self.server_id, self.role_id)

    @property
    def after(self):
        return self.client.cache.get_role(self.server_id, self.role_id)

    @property
    def role(self):
        return self.client.cache.get_role(self.server_id, self.role_id)


ServerRoleCreate = ServerRoleUpdate


class ServerRoleDelete(ServerEvent):
    event_type: str = field(alias='type', repr=False)
    server_id: str = field(alias='id')
    role_id: str


class UserUpdate(PyreEvent):
    event_type: str = field(alias='type', repr=False)
    user_id: str = field(alias='id')
    data: User = None
    clear: List[str] = None

    @property
    def before(self) -> User:
        return self.client.cache.get_deleted_user()


class UserRelationship(PyreEvent):
    event_type: str = field(alias='type', repr=False)
    user_id: str = field(alias='id')
    user: User
    status: RelationshipStatus


class UserPlatformWipe(PyreEvent):
    event_type: str = field(alias='type', repr=False)
    user_id: str
    flags: Any


class EmojiCreate(PyreEvent):
    event_type: str = field(alias='type', repr=False)
    id: str = field(alias='_id')
    creator_id: str
    name: str
    animated: Optional[bool] = False
    nsfw: Optional[bool] = False
    parent: ServerParent = None


class EmojiDelete(PyreEvent):
    event_type: str = field(alias='type', repr=False)
    id: str

EVENTS = [
    MessageCreate,
    MessageUpdate,
    MessageAppend,
    MessageDelete,
    MessageReact,
    MessageUnreact,
    MessageRemoveReaction,
    ChannelCreate,
    ChannelUpdate,
    ChannelDelete,
    ChannelGroupJoin,
    ChannelGroupLeave,
    ChannelStartTyping,
    ChannelStopTyping,
    ChannelAck,
    ServerCreate,
    ServerUpdate,
    ServerDelete,
    ServerMemberUpdate,
    ServerMemberJoin,
    ServerMemberLeave,
    ServerRoleUpdate,
    ServerRoleCreate,
    ServerRoleDelete,
    UserUpdate,
    UserRelationship,
    UserPlatformWipe,
    EmojiCreate,
    EmojiDelete
]

LISTENERS = Union[
    MessageCreate,
    MessageUpdate,
    MessageAppend,
    MessageDelete,
    MessageReact,
    MessageUnreact,
    MessageRemoveReaction,
    ChannelCreate,
    ChannelUpdate,
    ChannelDelete,
    ChannelGroupJoin,
    ChannelGroupLeave,
    ChannelStartTyping,
    ChannelStopTyping,
    ChannelAck,
    ServerCreate,
    ServerUpdate,
    ServerDelete,
    ServerMemberUpdate,
    ServerMemberJoin,
    ServerMemberLeave,
    ServerRoleUpdate,
    ServerRoleDelete,
    UserUpdate,
    UserRelationship,
    UserPlatformWipe,
    EmojiCreate,
    EmojiDelete
]
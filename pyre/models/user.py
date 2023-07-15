from typing import Optional, Any, List, TYPE_CHECKING, Annotated
from datetime import datetime
from pydantic import Field as field, WrapValidator
from .base import PyreObject
from .file import File
from pyre.enums import Permissions
if TYPE_CHECKING:
    from .server import Server
    from .role import Role


class RelationshipStatus(PyreObject):
    _id: str
    status: str  # = 'None' | "User" | "Friend" | "Outgoing" | "Incoming" | "Blocked" | "BlockedOther"


class Status(PyreObject):
    text: Optional[str] = None
    presence: Optional[str] = None


class UserProfile(PyreObject):
    content: Optional[str] = None
    background: Optional[File] = None


class User(PyreObject):
    id: Optional[str] = field(alias='_id', default=None)
    username: Optional[str] = None
    discriminator: Optional[str] = None
    display_name: Optional[str] = None
    avatar_info: Optional[File] = field(alias='avatar', default=None)
    relations: Optional[RelationshipStatus] = None
    badges: Optional[int] = None
    status: Optional[Status] = None
    profile: Optional[UserProfile] = None
    flags: Optional[int] = None
    privileged: Optional[bool] = False
    bot: Optional[Any] = None
    relationship: Optional[Any] = None
    online: Optional[bool] = False

    @property
    def avatar(self) -> str:
        """The avatar url"""
        if self.avatar_info is None:
            return f"https://app.revolt.chat/api/users/{self.id}/default_avatar"
        return f'https://autumn.revolt.chat/avatars/{self.avatar_info.id}'

    @property
    def servers(self) -> List["Server"]:
        """Servers the user and bot share"""
        all_servers = self.client.cache.get_servers()
        servers = []
        for server in all_servers:
            if self.client.cache.get_member(server.id, self.id):
                servers.append(server)
        if servers:
            return servers
        return None


class BotUser(PyreObject):
    id: str = field(alias='_id')
    owner: str
    token: str
    public: bool = False
    analytics: Optional[bool] = False
    discoverable: Optional[bool] = False
    interactions_url: Optional[str] = None
    terms_of_service_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    flags: Optional[int] = None


class MemberIds(PyreObject):
    server_id: str = field(alias='server')
    user_id: str = field(alias='user')


class PartialMember(PyreObject):
    nickname: Optional[str] = None
    avatar_info: Optional[File] = field(alias='avatar', default=None)
    role_ids: Optional[List[str]] = field(alias='roles', default=None)
    timeout: Optional[datetime] = None

class Member(PyreObject):
    ids: MemberIds = field(alias='_id', default=None)
    joined_at: datetime = None
    nick: Optional[str] = field(alias="nickname", default=None)
    avatar_info: Optional[File] = field(alias='avatar', default=None)
    role_ids: Optional[List[str]] = field(alias='roles', default=None)
    timeout: Optional[datetime] = None

    @property
    def nickname(self) -> str:
        if self.nick is None:
            return self.user.username
        return self.nick

    @property
    def avatar(self) -> str:
        """Avatar url"""
        return f'https://autumn.revolt.chat/avatars/{self.avatar_info.id}'

    @property
    def server(self) -> "Server":
        """The server this member is part of"""
        return self.client.cache.get_server(self.ids.server_id)

    @property
    def user(self) -> User:
        """The members user"""
        return self.client.cache.get_user(self.ids.user_id)

    @property
    def bot(self) -> bool:
        """Is member a bot"""
        if self.user.bot:
            return True
        return False

    @property
    def id(self) -> str:
        """Member ID"""
        return self.ids.user_id

    @property
    def server_id(self) -> str:
        """Members server ID"""
        return self.ids.server_id

    @property
    def is_owner(self) -> bool:
        """Whether the member is the server owner"""
        if self.id == self.server.owner_id:
            return True
        return False

    @property
    def roles(self) -> List["Role"]:
        roles = [self.client.cache.get_role(
            self.server_id, role_id) for role_id in self.role_ids]
        return sorted(roles, key=lambda role: role.rank)

    @property
    def permissions(self) -> List[Permissions]:
        """Members allowed permissions"""
        if self.is_owner:
            all_val = Permissions.all()
            return Permissions.get_permissions(all_val)
        allows = []
        for role in self.roles:
            for perm in role.permissions:
                if perm not in allows:
                    allows.append(perm)

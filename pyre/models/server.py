from typing import Optional, Any, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field as field
from .base import PyreObject
from .role import Role
from .file import File
if TYPE_CHECKING:
    from .user import Member


class Category(PyreObject):
    id: str
    title: str
    channels: List[str]


class Server(PyreObject):
    id: str = field(alias='_id', default=None)
    owner_id: str = field(alias='owner', default=None)
    name: str = None
    channel_ids: List[str] = field(alias='channels', default=None)
    default_permissions: int = None
    description: Optional[str] = None
    categs: Optional[Any] = field(alias='categories', default=None)
    system_messages: Optional[Any] = None
    raw_roles: Optional[Any] = field(alias='roles', default=None)
    icon: Optional[File] = None
    banner: Optional[File] = None
    flags: Optional[int] = None
    nsfw: Optional[bool] = False
    analytics: Optional[bool] = False
    discoverable: Optional[bool] = False

    @property
    def channels(self):
        return [self.client.cache.get_channel(channel_id) for channel_id in self.channel_ids]

    @property
    def categories(self) -> List[Category]:
        return [Category(**categ, wsclient=self.wsclient) for categ in self.categs]

    @property
    def roles(self) -> List[Role]:
        roles = self.client.cache.getraw_roles(self.id)
        return sorted(roles, key=lambda role: role.rank)

    @property
    def members(self) -> List["Member"]:
        return self.client.cache.get_members(self.id)

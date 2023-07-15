from typing import Optional, Any, List, Tuple, Union
from pydantic import Field as field
from .base import PyreObject, SendableObject
from .file import File


class BaseChannel(PyreObject):
    event_type: str = field(alias='type', repr=False, default=None)
    channel_type: str = None
    id: str = field(alias='_id', default=None)

class BaseTextChannel(SendableObject):
    """Base channel for text channels"""
    event_type: str = field(alias='type', repr=False, default=None)
    channel_type: str = None
    id: str = field(alias='_id', default=None)

class SavedMessage(BaseChannel):
    user_id: str = field(alias='user', default=None)


class DMChannel(BaseTextChannel):
    active: bool = False
    recipients: List[Tuple[str, str]] = None
    last_message_id: Optional[str] = None


class GroupChannel(BaseTextChannel):
    name: str = None
    recipients: List[str] = None
    owner_id: str = field(alias="owner", default=None)
    description: Optional[str] = None
    icon: Optional[File] = None
    last_message_id: Optional[str] = None
    permissions: Optional[int] = None
    nsfw: Optional[bool] = False


class DefaultPermission(PyreObject):
    a: int = 0
    d: int = 0


class RolePermission(PyreObject):
    a: int = 0
    d: int = 0
    role_id: Optional[str] = None


class TextChannel(BaseTextChannel):
    server_id: str = field(alias="server", default=None)
    name: str = None
    description: Optional[str] = None
    icon: Optional[File] = None
    last_message_id: str = None
    default_permissions: Optional[DefaultPermission] = None
    role_perms: Optional[Any] = field(alias='role_permissions',
                                             default=None)
    nsfw: Optional[bool] = False

    @property
    def server(self):
        return self.client.cache.get_server(self.server_id)

    @property
    def role_permissions(self) -> List[RolePermission]:
        if self.role_perms is None:
            return None
        else:
            perms_list = []
            perms_dict = self.role_perms
            role_ids = perms_dict.keys()
            for role_id in role_ids:
                role_dict = perms_dict.get(role_id)
                perms_list.append(
                    RolePermission(wsclient=self.wsclient,
                                   role_id=role_id,
                                   **role_dict))
            return perms_list


class VoiceChannel(BaseChannel):
    server_id: str = field(alias="server", default=None)
    name: str = None
    description: Optional[str] = None
    icon: Optional[File] = None
    default_permissions: Optional[DefaultPermission] = None
    role_perms: Optional[Any] = field(alias='role_permissions',
                                             default=None)
    nsfw: Optional[bool] = False

    @property
    def server(self):
        return self.client.cache.get_server(self.server_id)

    @property
    def role_permissions(self) -> List[RolePermission]:
        if self.role_perms is None:
            return None
        else:
            perms_list = []
            perms_dict = self.role_perms
            role_ids = perms_dict.keys()
            for role_id in role_ids:
                role_dict = perms_dict.get(role_id)
                perms_list.append(
                    RolePermission(wsclient=self.wsclient,
                                   role_id=role_id,
                                   **role_dict))
            return perms_list


TYPE_ALL_CHANNEL = Union[TextChannel, DMChannel, VoiceChannel, GroupChannel,
                         SavedMessage]

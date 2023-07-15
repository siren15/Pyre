from typing import Optional, List, TYPE_CHECKING
from pydantic import Field as field
from pydantic_extra_types import color
from .base import PyreObject
from pyre.enums import Permissions
if TYPE_CHECKING:
    from .server import Server


class PermissionOverride(PyreObject):
    a: int = 0
    d: int = 0


class BaseRole(PyreObject):
    name: str = None
    permissions_override: PermissionOverride = field(alias='permissions', default=PermissionOverride(a=0, d=0))
    colour: Optional[color.Color] = color.Color('ff4655')
    show_separately: bool = field(alias='hoist', default=False)
    rank: Optional[int] = 0


class Role(BaseRole):
    id: str = None
    server_id: str = None

    @property
    def server(self) -> "Server":
        """The server this role is from"""
        return self.client.cache.get_server(self.server_id)

    @property
    def allowed_permissions(self) -> List[Permissions]:
        """List of allowed permissions"""
        return Permissions.get_permissions(self.permissions_override.a)

    @property
    def denied_permissions(self) -> List[Permissions]:
        """List of denied permissions"""
        return Permissions.get_permissions(self.permissions_override.d)

    @property
    def permissions(self) -> List[Permissions]:
        """Role permissions"""
        if self.is_owner:
            all_val = Permissions.all()
            return Permissions.get_permissions(all_val)
        allows = []
        server_default_perms = Permissions.get_permissions(
            self.server.default_permissions)
        allows += server_default_perms
        for perm in self.allowed_permissions:
            if perm not in allows:
                allows.append(perm)
        return [perm for perm in allows if perm not in self.denied_permissions]
from enum import Enum
from typing import List

class Permissions(Enum):
    """Permissions a user or role may have."""
    MANAGE_CHANNEL = 1 << 0
    """Manage the channel or channels on the server"""
    MANAGE_SERVER = 1 << 1
    """Manage the server"""
    MANAGE_PERMISSIONS = 1 << 2
    """Manage permissions on servers or channels"""
    MANAGE_ROLES = 1 << 3
    """Manage roles on server"""
    MANAGE_CUSTOMISATION = 1 << 4
    """Manage emojis on servers"""
    KICK_MEMBERS = 1 << 6
    """Kick other members below their ranking"""
    BAN_MEMBERS = 1 << 7
    """Ban other members below their ranking"""
    TIMEOUT_MEMBERS = 1 << 8
    """Timeout other members below their ranking"""
    ASSIGN_ROLES = 1 << 9
    """Assign roles to members below their ranking"""
    CHANGE_NICKNAME = 1 << 10
    """Change own nickname"""
    CHANGE_NICKNAMES = 1 << 11
    """Change or remove other's nicknames below their ranking"""
    CHANGE_AVATAR = 1 << 12
    """Change own avatar"""
    REMOVE_AVATARS = 1 << 13
    """Remove other's avatars below their ranking"""
    VIEW_CHANNEL = 1 << 20
    """View a channel"""
    READ_MESSAGE_HISTORY = 1 << 21
    """Read a channel's past message history"""
    SEND_MESSAGE = 1 << 22
    """Send a message in a channel"""
    MANAGE_MESSAGES = 1 << 23
    """Delete messages in a channel"""
    MANAGE_WEBHOOKS = 1 << 24
    """Manage webhook entries on a channel"""
    INVITE_OTHERS = 1 << 25
    """Create invites to this channel"""
    SEND_EMBEDS = 1 << 26
    """Send embedded content in this channel"""
    UPLOAD_FILES = 1 << 27
    """Send attachments and media in this channel"""
    MASQUERADE = 1 << 28
    """Masquerade messages using custom nickname and avatar"""
    REACT = 1 << 29
    """React to messages with emojis"""
    CONNECT = 1 << 30
    """Connect to a voice channel"""
    SPEAK = 1 << 31
    """Speak in a voice call"""
    VIDEO = 1 << 32
    """Share video in a voice call"""
    MUTE_MEMBERS = 1 << 33
    """Mute other members with lower ranking in a voice call"""
    DEAFEN_MEMBERS = 1 << 34
    """Deafen other members with lower ranking in a voice call"""
    MOVE_MEMBERS = 1 << 35
    """Move members between voice channels"""

    @classmethod
    def get_permissions(cls, permissions_value: int) -> List:
        """Permissions from a value"""
        present_permissions = []
        for enum_name, enum_value in cls.__members__.items():
            if permissions_value & enum_value.value > 0:
                present_permissions.append(cls[enum_name])
        return present_permissions

    @classmethod
    def set_permissions(cls, enum_members: List) -> int:
        """Permissions into a value"""
        enum_value = 0
        for enum_member in enum_members:
            enum_value |= enum_member.value
        return enum_value

    @classmethod
    def all(cls) -> int:
        """Value of all permissions"""
        return cls.set_permissions([perm[1] for perm in cls.__members__.items()])

class UserRemove(Enum):
    AVATAR = 'Avatar'
    STATUS_TEXT = 'StatusText'
    STATUS_PRESENCE = 'StatusPresence'
    PROFILE_CONTENT = 'ProfileContent'
    PROFILE_BACKGROUND = 'ProfileBackground'
    DISPLAY_NAME = 'DisplayName'

class ChannelRemove(Enum):
    DESCRIPTION = 'Description'
    ICON = "Icon"
    DEFAULT_PERMISSIONS = 'DefaultPermissions'
    
class MessageSort(Enum):
    RELEVANCE = 'Relevance'
    LATEST = 'Latest'
    OLDEST = 'Oldest'
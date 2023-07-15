from cacheout import CacheManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cacheout import Cache


class ClientCache:

    def __init__(self):
        self.ttl = 60
        self.hard_limit = 256
        self.maxsize = 0
        self.cache = CacheManager({
            'users': {
                'maxsize': self.maxsize
            },
            'members': {
                'maxsize': self.maxsize
            },
            'channels': {
                'maxsize': self.maxsize
            },
            'servers': {
                'maxsize': self.maxsize
            },
            'messages': {
                'ttl': 60 * 60 * 24 * 7,
                'maxsize': self.maxsize
            },
            'roles': {
                'maxsize': self.maxsize
            },
            'emoji': {
                'maxsize': self.maxsize
            },
            'bot': {
                'maxsize': self.maxsize
            },
            'deleted': {
                'maxsize': self.hard_limit,
                'ttl': self.ttl
            }
        })
        self.users: "Cache" = self.cache['users']
        self.members: "Cache" = self.cache['members']
        self.channels: "Cache" = self.cache['channels']
        self.servers: "Cache" = self.cache['servers']
        self.messages: "Cache" = self.cache['messages']
        self.roles: "Cache" = self.cache['roles']
        self.emoji: "Cache" = self.cache['emoji']
        self.bot: "Cache" = self.cache['bot']
        self.deleted_members: "Cache" = self.cache["deleted"]
        self.deleted_messages: "Cache" = self.cache["deleted"]
        self.deleted_roles: "Cache" = self.cache["deleted"]
        self.deleted: "Cache" = self.cache["deleted"]

    def get_member(self, server_id: str, member_id: str):
        return self.members.get((server_id, member_id))

    def get_members(self, server_id: str):
        return [
            member for member in list(self.members.values())
            if member.server_id == server_id
        ]

    def get_channel(self, channel_id: str):
        return self.channels.get(channel_id)

    def get_channels(self, server_id: str):
        server = self.get_server(server_id)
        return server.channels

    def get_role(self, server_id: str, role_id: str):
        return self.roles.get((server_id, role_id))

    def get_roles(self, server_id):
        return [
            role for role in list(self.roles.values())
            if role.server_id == server_id
        ]

    def get_server(self, server_id: str):
        return self.servers.get(server_id)

    def get_servers(self):
        return [server for server in list(self.servers.values())]

    def get_user(self, user_id: str):
        return self.users.get(user_id)

    def get_message(self, channel_id: str, message_id: str):
        return self.messages.get((channel_id, message_id))

    def get_deleted_member(self, server_id: str, member_id: str):
        return self.deleted_members.get((server_id, member_id))

    def get_deleted_user(self, user_id: str):
        return self.deleted_members.get(user_id)

    def delete_user_from_cache(self, user_id: str):
        user = self.get_user(user_id)
        self.deleted_members.set(user_id, user)
        self.users.delete(user_id)

    def get_deleted_message(self, channel_id: str, message_id: str):
        return self.deleted_messages.get((channel_id, message_id))

    def delete_message_from_cache(self, channel_id: str, message_id: str):
        keys = (channel_id, message_id)
        message = self.get_message(channel_id, message_id)
        self.deleted_messages.set(keys, message)
        self.messages.delete(keys)

    def delete_member_from_cache(self, server_id: str, member_id: str):
        member = self.get_member(server_id, member_id)
        self.deleted_members.set((server_id, member_id), member)
        self.members.delete((server_id, member_id))

    def delete_role_in_cache(self, server_id: str, role_id: str):
        role = self.get_role(server_id, role_id)
        self.deleted_roles.set((server_id, role.id), role)
        self.roles.delete((server_id, role.id))

    def get_deleted_role(self, server_id: str, role_id: str):
        return self.deleted_roles.get((server_id, role_id))

    def get_deleted_channel(self, channel_id: str):
        return self.deleted.get(channel_id)

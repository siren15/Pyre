import asyncio
from .ws import WSClient
import pyre.models as models
from pydantic_extra_types import color
from typing import List
import re


class PyreClient:

    def __init__(self, token:str, prefixes:List[str]=None):
        self.token = token
        self.ws = WSClient(self.token)
        self.cache = self.ws.cache
        self.ws.client = self
        self.http = self.ws.http
        self.events = self.ws.events
        self.default_events = self.ws.default_events
        self.http.client = self
        self.prefixes = prefixes


    async def astart(self):
        self.register_default_listeners()
        await self.http.login()
        await self.ws.connect()

    def start(self):
        asyncio.run(self.astart())

    def listen(self, model: models.PyreEvent):

        def decorator(callback):
            if not asyncio.iscoroutinefunction(callback):
                raise TypeError("Listener must be a coroutine")
            event_name = model.__name__
            listener = models.Listener(event_name, model, callback)
            self.events.append(listener)
            return callback

        return decorator

    def register_default_listeners(self):
        self.ws.add_default_event(models.Message, self.cache_messages)
        self.ws.add_default_event(models.MessageUpdate, self.cache_messages)
        self.ws.add_default_event(models.MessageDelete, self.cache_messages)
        #
        self.ws.add_default_event(models.ServerMemberJoin, self.cache_members)
        self.ws.add_default_event(models.ServerMemberUpdate,
                                  self.cache_members)
        self.ws.add_default_event(models.ServerMemberLeave, self.cache_members)
        self.ws.add_default_event(models.UserPlatformWipe, self.cache_members)
        self.ws.add_default_event(models.UserUpdate, self.cache_members)
        #
        self.ws.add_default_event(models.ServerRoleUpdate, self.cache_roles)
        self.ws.add_default_event(models.ServerRoleDelete, self.cache_roles)
        #
        self.ws.add_default_event(models.ChannelCreate, self.cache_channels)
        self.ws.add_default_event(models.ChannelUpdate, self.cache_channels)
        self.ws.add_default_event(models.ChannelDelete, self.cache_channels)
        #
        self.ws.add_default_event(models.ServerCreate, self.cache_servers)
        self.ws.add_default_event(models.ServerUpdate, self.cache_servers)
        self.ws.add_default_event(models.ServerDelete, self.cache_servers)

    @property
    def user(self) -> models.User:
        """The client user"""
        return self.cache.bot.get('me')

    @property
    def servers(self) -> List[models.Server]:
        """List of all servers"""
        return list(self.cache.servers.values())

    async def latency(self) -> int:
        """Returns the latency of the websocket connection (seconds)."""
        ping = await self.ws.websocket.ping()
        return await ping

    async def cache_messages(self, event):
        if isinstance(event, models.Message):
            msg = models.TextMessage(wsclient=self)
            for n, v in event:
                attr = getattr(msg, n, None)
                if not attr and hasattr(msg, n):
                    setattr(msg, n, v)
            self.cache.messages.set((event.channel_id, event.id), msg)

        elif isinstance(event, models.MessageUpdate):
            old_msg = self.cache.get_message(event.channel_id, event.message_id)
            new_msg = event.data
            for n, v in old_msg:
                attr = getattr(new_msg, n, None)
                if not attr and hasattr(new_msg, n):
                    setattr(new_msg, n, v)

            keys = (event.channel_id, event.message_id)
            self.cache.deleted.set(keys, old_msg)
            self.cache.messages.delete(keys)
            self.cache.messages.set(keys, new_msg)

        elif isinstance(event, models.MessageDelete):
            self.cache.delete_message_from_cache(event.message_id,
                                                 event.channel_id)

    async def cache_members(self, event):
        if isinstance(event, models.ServerMemberJoin):
            user = self.http.fetch_user(event.user_id)
            member = self.http.fetch_member(event.server_id, event.user_id)
            self.cache.users.set(user['_id'], models.User(wsclient=self,
                                                          **user))
            self.cache.members.set((event.server_id, event.user_id),
                                   models.Member(wsclient=self, **member))

        elif isinstance(event, models.ServerMemberUpdate):
            old_member = self.cache.get_member(event.ids.server_id, event.ids.user_id)
            new_member = event.data
            clear = event.clear
            for n, v in old_member:
                attr = getattr(new_member, n, None)
                if not attr and hasattr(new_member, n):
                    setattr(new_member, n, v)

            if 'Avatar' in clear:
                new_member.avatar_info = new_member.user.avatar_info
            if 'Nickname' in clear:
                new_member.nick = new_member.user.username
            
            keys = (event.ids.server_id, event.ids.user_id)
            self.cache.deleted.set(keys, old_member)
            self.cache.members.delete(keys)
            self.cache.members.set(keys, new_member)

        elif isinstance(event, models.ServerMemberLeave):
            user = self.cache.get_user(event.user_id)
            if len(user.servers) <= 1:
                self.cache.delete_user_from_cache(user.id)
            self.cache.delete_member_from_cache(event.server_id, event.user_id)

        elif isinstance(event, models.UserPlatformWipe):
            for server in self.servers:
                self.cache.delete_member_from_cache(server.id, event.user_id)
            self.cache.delete_user_from_cache(event.user_id)

        elif isinstance(event, models.UserUpdate):
            old_user = self.cache.get_user(event.user_id)
            new_user = event.data
            clear = event.clear
            for n, v in old_user:
                attr = getattr(new_user, n, None)
                if not attr and hasattr(new_user, n):
                    setattr(new_user, n, v)

            if "ProfileContent" in clear:
                new_user.profile.content = None
            if "ProfileBackground" in clear:
                new_user.profile.background = None
            if "StatusText" in clear:
                new_user.status.text = None
            if "Avatar" in clear:
                new_user.avatar_info = None

            self.cache.deleted.set(event.user_id, old_user)
            self.cache.users.delete(event.user_id)
            self.cache.users.set(event.user_id, new_user)

    async def cache_roles(self, event):
        if isinstance(event, models.ServerRoleUpdate):
            old_role = self.cache.get_role(event.server_id, event.role_id)
            new_role = event.data
            clear = event.clear
            if old_role:
                self.cache.deleted.set((event.server_id, event.role_id), old_role)
                self.cache.roles.delete((event.server_id, event.role_id))
                for n, v in old_role:
                    attr = getattr(new_role, n, None)
                    if not attr and hasattr(new_role, n):
                        setattr(new_role, n, v)

            if 'Colour' in clear:
                new_role.colour = color.Color('ff4655')
            self.cache.roles.set((event.server_id, event.role_id), new_role)

        elif isinstance(event, models.ServerRoleDelete):
            self.cache.delete_role_in_cache(event.server_id, event.role_id)

    async def cache_channels(self, event):
        if isinstance(event, models.ChannelCreate):
            self.cache.channels.set(event.channel.id, event.channel)

        elif isinstance(event, models.ChannelUpdate):
            old_channel = self.cache.get_channel(event.channel_id)
            new_channel = event.data
            clear = event.clear
            for n, v in old_channel:
                attr = getattr(new_channel, n, None)
                if not attr and hasattr(new_channel, n):
                    setattr(new_channel, n, v)

            if 'Icon' in clear:
                new_channel.icon = None
            if 'Description' in clear:
                new_channel.description = None
            self.cache.deleted.set(event.channel_id, old_channel)
            self.cache.channels.delete(event.channel_id)
            self.cache.channels.set(event.channel_id, new_channel)

        elif isinstance(event, models.ChannelDelete):
            self.cache.channels.delete(event.channel_id)

    async def cache_servers(self, event):
        if isinstance(event, models.ServerCreate):
            self.cache.servers.set(event.server_id, event.server)

        elif isinstance(event, models.ServerUpdate):
            old_server = self.cache.get_server(event.server_id)
            new_server = event.data
            clear = event.clear
            for n, v in old_server:
                attr = getattr(new_server, n, None)
                if not attr and hasattr(new_server, n):
                    setattr(new_server, n, v)

            if 'Icon' in clear:
                new_server.icon = None
            if 'Banner' in clear:
                new_server.banner = None
            if 'Description' in clear:
                new_server.description = None
            self.cache.deleted.set(event.server_id, old_server)
            self.cache.servers.delete(event.server_id)
            self.cache.servers.set(event.server_id, new_server)

        elif isinstance(event, models.ServerDelete):
            server = self.cache.get_server(event.server_id)
            for member in server.members:
                self.cache.members.delete((server.id, member.id))
                if len(member.user.servers) <= 1:
                    self.cache.users.delete(member.id)
            for channel in server.channels:
                self.cache.channels.delete(channel.id)
            for role in server.roles:
                self.cache.roles.delete((server.id, role.id))
            for channel in server.channels:
                idr = r"^[a-zA-Z0-9_-]+$"
                self.cache.messages.delete_many((channel.id, re.compile(idr)))

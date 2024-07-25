import asyncio
import inspect

from .logger import LOG
from .models import (
    BaseCommand, 
    PyreEvent,
    Listener,
    CommandContext,
    CommandArg,
    User,
    Server,
    MessageCreate,
    TextMessage,
    MessageUpdate,
    MessageDelete,
    ServerMemberJoin,
    ServerMemberJoin,
    ServerMemberUpdate,
    ServerMemberLeave,
    Member,
    UserPlatformWipe,
    UserUpdate,
    ServerRoleUpdate,
    ServerRoleDelete,
    ChannelCreate,
    ChannelUpdate,
    ChannelDelete,
    ServerCreate,
    ServerUpdate,
    ServerDelete,
    EVENTS_ALL
)
import re

from pydantic_extra_types import color
from typing import List

from .ws import WSClient, DEFAULT_EVENTS
from .enums import Permissions
from .errors import PermissionError, ValidationError
from .utils import correct_event_name_formatting

class PyreClient:
    """The bot client.
    Args:
        token (str): The bot token.
        prefixes (List[str]): The bot prefixes.
    """
    def __init__(self, token: str, prefixes: List[str] = []):
        self.token = token
        self.ws = WSClient(self.token)
        self.cache = self.ws.cache
        self.ws.client = self
        self.http = self.ws.http
        self.events = self.ws.events
        self.default_events = self.ws.default_events
        self.http.client = self
        self.prefixes = prefixes
        self.commands: List[BaseCommand] = []
        self.extensions = []

    async def astart(self):
        await self.ws.connect()

    def start(self):
        """Start the client"""
        asyncio.run(self.astart())

    def listen(self, event: PyreEvent = None):
        """
        The listen function is a decorator that allows you to listen for events.
        It takes in event as an argument, and returns the callback function with the event name and model attached to it.
        The event name is used by Pyre when sending out events, so that only listeners listening for that specific event will be called.
        
        Args:
            event (PyreEvent): Specify the type of event that will be listened for
        
        Returns:
            A decorator, which is a function that takes in another function and returns it
        """

        def decorator(callback):
            if not asyncio.iscoroutinefunction(callback):
                raise TypeError("Listener must be a coroutine")
            event_name = event.__name__ if event else correct_event_name_formatting(callback.__name__)
            name = 'Message' if event_name == 'MessageCreate' else event_name
            event_model = event if event else next((e for e in EVENTS_ALL if e.__name__ == event_name), None)
            if not event_model:
                raise ValidationError(f'Listener event not found for {callback.__name__}')
            listener = Listener(name, event_model, callback)
            self.events.append(listener)
            return callback
        return decorator
    
    def register_default_listener(model: PyreEvent):
        def decorator(callback):
            if not asyncio.iscoroutinefunction(callback):
                raise TypeError("Listener must be a coroutine")
            event_name = model.__name__
            name = 'Message' if event_name == 'MessageCreate' else event_name
            listener = Listener(name, model, callback)
            DEFAULT_EVENTS.append(listener)
            return callback
        return decorator

    def command(
        self,
        name: str = None,
        description: str = "No description",
        aliases: List[str] = [],
        default_permissions: List[Permissions] = [],
    ):
        """A decorator that allows you to register a command.
        Args:
            self: Refer to the object itself
            name: str: The name of the command
            description: str: The description of the command
            aliases: List[str]: The aliases of the command
            default_permissions: List[Permissions]: The permissions Members will have to have to run the command
        """

        def decorator(callback):
            if not asyncio.iscoroutinefunction(callback):
                raise TypeError("Command must be a coroutine")

            command_name = callback.__name__ if not name else name

            # Use inspect to get the function's parameters and their names
            signature = inspect.signature(callback)
            args = []

            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                if not issubclass(param.annotation, CommandContext):
                    arg = CommandArg(
                        name=param_name,
                        type=param.annotation if param.annotation
                        != inspect.Parameter.empty else str)
                    args.append(arg)
            # Create and register the command
            cmd = BaseCommand(wsclient=self.ws,
                                     name=command_name,
                                     description=description,
                                     aliases=aliases,
                                     args=args,
                                     callback=callback,
                                     default_permissions=default_permissions)
            self.commands.append(cmd)

            # Return the original callback
            return callback

        return decorator

    @property
    def user(self) -> User:
        """The client user"""
        return self.cache.bot.get('me')

    @property
    def servers(self) -> List[Server]:
        """List of all servers"""
        return list(self.cache.servers.values())

    async def latency(self) -> int:
        """Returns the latency of the websocket connection (seconds)."""
        ping = await self.ws.websocket.ping()
        return await ping
    
    @register_default_listener(MessageCreate)
    async def cache_messages_created(self, event: MessageCreate):
        msg = TextMessage(wsclient=self)
        for n, v in event:
            attr = getattr(msg, n, None)
            if not attr and hasattr(msg, n):
                setattr(msg, n, v)
        self.cache.messages.set((event.channel_id, event.id), msg)
    
    @register_default_listener(MessageUpdate)
    async def cache_messages_updated(self, event: MessageUpdate):
        old_msg = self.cache.get_message(event.channel_id,
                                            event.message_id)
        new_msg = event.data
        for n, v in old_msg:
            attr = getattr(new_msg, n, None)
            if not attr and hasattr(new_msg, n):
                setattr(new_msg, n, v)

        keys = (event.channel_id, event.message_id)
        self.cache.deleted.set(keys, old_msg)
        self.cache.messages.delete(keys)
        self.cache.messages.set(keys, new_msg)

    @register_default_listener(MessageDelete)
    async def cache_messages_deleted(self, event:MessageDelete):
        self.cache.delete_message_from_cache(event.message_id,
                                                event.channel_id)

    @register_default_listener(ServerMemberJoin)
    async def cache_members_join(self, event:ServerMemberJoin):
        user = self.http.fetch_user(event.user_id)
        member = self.http.fetch_member(event.server_id, event.user_id)
        self.cache.users.set(user['_id'], User(wsclient=self,
                                                        **user))
        self.cache.members.set((event.server_id, event.user_id),
                                Member(wsclient=self, **member))
    
    @register_default_listener(ServerMemberUpdate)
    async def cache_members_update(self, event:ServerMemberUpdate):
        old_member = self.cache.get_member(event.ids.server_id,
                                            event.ids.user_id)
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

    @register_default_listener(ServerMemberLeave)
    async def cache_members_leave(self, event:ServerMemberLeave):
        user = self.cache.get_user(event.user_id)
        if len(user.servers) <= 1:
            self.cache.delete_user_from_cache(user.id)
        self.cache.delete_member_from_cache(event.server_id, event.user_id)

    @register_default_listener(UserPlatformWipe)
    async def cache_members_platform_wipe(self, event:UserPlatformWipe):
        for server in self.servers:
            self.cache.delete_member_from_cache(server.id, event.user_id)
        self.cache.delete_user_from_cache(event.user_id)

    @register_default_listener(UserUpdate)
    async def cache_users_update(self, event:UserUpdate):
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

    @register_default_listener(ServerRoleUpdate)
    async def cache_roles_update(self, event: ServerRoleUpdate):
        old_role = self.cache.get_role(event.server_id, event.role_id)
        new_role = event.data
        clear = event.clear
        if old_role:
            self.cache.deleted.set((event.server_id, event.role_id),
                                    old_role)
            self.cache.roles.delete((event.server_id, event.role_id))
            for n, v in old_role:
                attr = getattr(new_role, n, None)
                if not attr and hasattr(new_role, n):
                    setattr(new_role, n, v)

        if 'Colour' in clear:
            new_role.colour = color.Color('ff4655')
        self.cache.roles.set((event.server_id, event.role_id), new_role)
    
    @register_default_listener(ServerRoleDelete)
    async def cache_roles_delete(self, event: ServerRoleDelete):
        self.cache.delete_role_in_cache(event.server_id, event.role_id)

    @register_default_listener(ChannelCreate)
    async def cache_channels_create(self, event:ChannelCreate):
        self.cache.channels.set(event.channel.id, event.channel)

    @register_default_listener(ChannelUpdate)
    async def cache_channels_upddate(self, event:ChannelUpdate):
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

    @register_default_listener(ChannelDelete)
    async def cache_channels_delete(self, event: ChannelDelete):
        self.cache.channels.delete(event.channel_id)

    @register_default_listener(ServerCreate)
    async def cache_servers_create(self, event: ServerCreate):
        self.cache.servers.set(event.server_id, event.server)

    @register_default_listener(ServerUpdate)
    async def cache_servers_update(self, event: ServerUpdate):
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

    @register_default_listener(ServerDelete)
    async def cache_servers_delete(self, event: ServerDelete):
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

    def load_extension(self, extension_name):
        try:
            extension = __import__(extension_name)
            self.extensions.append(extension)
            LOG.info(f'Extension {extension_name} loaded successfully.')
        except Exception as e:
            LOG.error(f'Failed to load extension {extension_name}: {e}')

    def unload_extension(self, extension_name):
        try:
            self.extensions.remove(extension_name)
            LOG.info(f'Extension {extension_name} unloaded successfully.')
        except ValueError:
            LOG.error(f'Extension {extension_name} not found.')

    @register_default_listener(MessageCreate)
    async def resolve_command(self, event: MessageCreate):
        if event.author.bot or event.webhook:
            return
        content = event.content
        if not content:
            return
        prefix = next(
            (prefix for prefix in self.prefixes if content.startswith(prefix)),
            None)
        if prefix:
            args = content.removeprefix(prefix).split(" ")
            command = next(
                (cmd for cmd in self.commands if cmd.name == args[0]), None)
            if not command:
                return
            if command and not len(command.default_permissions) == len([
                    perm for perm in event.author.permissions
                    if perm in command.default_permissions
            ]):
                raise PermissionError(
                    "You don't have permission to use this command.")
            subcmd = next((cmd for cmd in self.commands
                           if len(args) > 1 and cmd.subcommand == args[1]),
                          None)
            if command and subcmd:
                args = args[2:]
            elif command and not subcmd:
                args = args[1:]
            ctx = CommandContext(wsclient=self.ws,
                                        command=command,
                                        server_id=event.server.id,
                                        author_id=event.author_id,
                                        channel_id=event.channel_id,
                                        message_id=event.id)
            verified_args = {}
            for arg in args:
                for cmd_arg in command.args:
                    if not issubclass(type(arg), cmd_arg.type):
                        raise ValidationError("Invalid argument type.")
                    verified_args[f"{cmd_arg.name}"] = arg
            await command.callback(ctx, **verified_args)

import asyncio
import inspect
import json
import functools

from typing import List, TYPE_CHECKING
from websockets import client as  ws_client
from .errors import LabelMe, InternalError, InvalidSession, OnboardingNotFinished, AlreadyAuthenticated
from .models import TextChannel, VoiceChannel, Server, User, Member, Role, Listener
from .cache import ClientCache
from .http import HTTPClient
from .logger import LOG

if TYPE_CHECKING:
    from .client import PyreClient

DEFAULT_EVENTS: List[Listener] = list()
EVENTS: List[Listener] = list()

class WSClient:
    def __init__(self, token: str, version: int = 1):
        self.url = 'wss://ws.revolt.chat'
        self.token = token
        self.version = version
        self.websocket = None
        self.events = EVENTS
        self.default_events = DEFAULT_EVENTS
        self.cache = ClientCache()
        self.http = HTTPClient(self.token)
        self.client: 'PyreClient' = None

    async def connect(self):
        try:
            self.websocket = await ws_client.connect(
                uri=f"{self.url}?token={self.token}&version={self.version}")
        except Exception as e:
            LOG.error(e)

        while True:
            message = await self.websocket.recv()
            await self.handle_message(message)

    async def handle_message(self, message):
        event = json.loads(message)
        if event['type'] == "Bulk":
            for event in event['v']:
                await self._handle_message(event)
        else:
            await self._handle_message(event)

    async def _handle_message(self, event):
        event_type = event.get("type")

        if event_type == "Error":
            self.handle_error(event.get("error"))
        elif event_type == "Authenticated":
            LOG.debug("Pyre lit!")
        elif event_type == "Ready":
            LOG.debug('Ready')
            await self.on_ready(event)
        else:
            await self.on_event(event)

    async def on_ready(self, event):
        for server in event['servers']:
            self.cache.servers.set(server['_id'],
                                   Server(wsclient=self.client, **server))
            
            roles_dict = server.get('roles')
            if roles_dict:
                role_ids = roles_dict.keys()
                for role_id in role_ids:
                    role_dict = roles_dict.get(role_id)
                    self.cache.roles.set((server['_id'], role_id), Role(wsclient=self.client, id=role_id, server_id=server['_id'], **role_dict))

            members = await self.http.fetch_members(server['_id'])
            for member in members['members']:
                self.cache.members.set((server['_id'], member['_id']['user']), Member(wsclient=self.client, **member))
                user = await self.http.fetch_user(member['_id']['user'])
                self.cache.users.set(user['_id'], User(wsclient=self.client, **user))
            
        for channel in event['channels']:
            if channel["channel_type"] == 'TextChannel':
                self.cache.channels.set(
                    channel['_id'], TextChannel(wsclient=self.client,
                                                **channel))
            elif channel["channel_type"] == 'VoiceChannel':
                self.cache.channels.set(
                    channel['_id'],
                    VoiceChannel(wsclient=self.client, **channel))

        # for emoji in event['emojis']:
        #     if emoji['parent']['type'] == 'Server':
        #         self.cache.emoji.set(
        #             emoji['_id'],
        #             ServerEmoji(wsclient=self.client, **emoji))
        #     elif emoji['parent']['type'] == 'Detached':
        #         self.cache.emoji.set(
        #             emoji['_id'],
        #             DetachedEmoji(wsclient=self.client, **emoji))

        me = await self.http.fetch_self()
        self.cache.bot.set('me', User(wsclient=self.client, **me))
        

        for listener in self.events:
            listener: Listener = listener
            if listener.name in ['ClientReady', 'OnReady', 'Ready']:
                await listener.callback()

    def handle_error(self, error_id):
        if error_id == 'LabelMe':
            raise LabelMe()
        elif error_id == "InternalError":
            raise InternalError()
        elif error_id == "InvalidSession":
            raise InvalidSession()
        elif error_id == "OnboardingNotFinished":
            raise OnboardingNotFinished()
        elif error_id == "AlreadyAuthenticated":
            raise AlreadyAuthenticated()
    
    def resolve_event_args(self, callback, event, payload):
        signature = inspect.signature(callback)
        args = {}
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                args['self'] = self.client
            else:
                args[param_name] = event(wsclient=self.client, **payload)
        return args

    async def on_event(self, raw_event: dict):
        event_name = raw_event['type']
        if event_name == "ChannelCreate":
            payload = {'channel':raw_event}
        else:
            payload = raw_event
        def_events = [functools.partial(listener.callback, **self.resolve_event_args(listener.callback, listener.event, payload)) for listener in self.default_events if listener.name == event_name]
        await asyncio.gather(*[func() for func in def_events])
        events = [functools.partial(listener.callback, **self.resolve_event_args(listener.callback, listener.event, payload)) for listener in self.events if listener.name == event_name]
        await asyncio.gather(*[func() for func in events])
import asyncio
import json
from websockets import client as  ws_client
from .errors import LabelMe, InternalError, InvalidSession, OnboardingNotFinished, AlreadyAuthenticated
from .models import SavedMessage, DMChannel, GroupChannel, TextChannel, VoiceChannel, ChannelCreate, Server, User, Member, ServerEmoji, DetachedEmoji, Role, Listener
from .cache import ClientCache
from .http import HTTPClient


class WSClient:

    def __init__(self, token: str, version: int = 1):
        self.url = 'wss://ws.revolt.chat'
        self.token = token
        self.version = version
        self.websocket = None
        self.events = []
        self.default_events = []
        self.cache = ClientCache()
        self.http = HTTPClient(self.token)
        self.client = None

    async def connect(self):
        try:
            self.websocket = await ws_client.connect(
                uri=f"{self.url}?token={self.token}&version={self.version}")
        except Exception as e:
            print(e)

        while True:
            message = await self.websocket.recv()
            await self.handle_message(message)

    async def handle_message(self, message):
        event = json.loads(message)
        if event['type'] == "Bulk":
            for event in message['v']:
                await self._handle_message(event)
        else:
            await self._handle_message(event)

    async def _handle_message(self, event):
        event_type = event.get("type")

        if event_type == "Error":
            self.handle_error(event.get("error"))
        elif event_type == "Authenticated":
            pass # print("Pyre lit!")
        elif event_type == "Ready":
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
        self.client.cache.bot.set('me', User(wsclient=self.client, **me))
        

        for listener in self.events:
            listener: Listener = listener
            if listener.name == 'ClientReady':
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

    async def on_event(self, raw_event: dict):
        event_name = raw_event['type']
        if event_name == "ChannelCreate":
            payload = {'channel':raw_event}
        else:
            payload = raw_event
        def_events = [listener.callback(listener.event(wsclient=self.client, **payload)) for listener in self.default_events if listener.name == event_name]
        await asyncio.gather(*def_events)
        events = [listener.callback(listener.event(wsclient=self.client, **payload)) for listener in self.events if listener.name == event_name]
        await asyncio.gather(*events)

    def add_event(self, event, callback):
        event_name = event.__name__
        listener = Listener(event_name, event, callback)
        self.events.append(listener)

    def add_default_event(self, event, callback):
        event_name = event.__name__
        listener = Listener(event_name, event, callback)
        self.default_events.append(listener)

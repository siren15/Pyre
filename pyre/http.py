from datetime import datetime
import httpx
import asyncio
from .errors import InvalidSession, HTTPError, InternalError
import pyre.models as models
from typing import Any, List, Literal
from .enums import UserRemove, ChannelRemove, Permissions, MessageSort
from .utils import validate_display_name, random_string_generator, validate_colour
from .logger import LOG
from httpx._types import (
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)

class HTTPClient:

    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://api.revolt.chat/'
        self.session = httpx.AsyncClient()
        self.client = None

    async def request(self, method: str, path: str, base_url: str = None, extra_headers: dict = None, content: RequestContent | None = None, data: RequestData | None = None, files: RequestFiles | None = None, json: Any | None = None, params: QueryParamTypes | None = None):
        if base_url:
            url = base_url + path
        else:
            url = self.base_url + path
        headers = {'X-Bot-Token': self.token}
        if extra_headers:
            headers.update(extra_headers)
        while True:
            response = await self.session.request(method, url, headers=headers, content=content, data=data, files=files, json=json, params=params)
            if response.status_code == 401:
                raise InvalidSession()
            elif response.status_code == 429:  # Rate limited
                retry_after = response.headers.get('X-RateLimit-Reset-After')
                if retry_after:
                    retry_after = int(retry_after) / 1000  # Convert to seconds
                    LOG.warn(f"Rate limited. Retrying after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                else:
                    LOG.warn("Rate limited. No 'X-RateLimit-Reset-After' header provided.")
            else:
                return response.json()

    async def close(self):
        """Close the aiohttp session."""
        await self.session.aclose()

    async def fetch_self(self):
        """Fetch thyself"""
        return await self.request('GET', 'users/@me')

    async def fetch_members(self,
                            server_id: str,
                            exclude_offline: bool = False):
        """
        Fetch all members of a server.

        Args:
            self: Represent the instance of the class
            server_id: str: Specify the server id of the server you want to fetch members from
            exclude_offline: bool: Exclude offline members from the response

        Returns:
            A list of members in the guild
        """

        data = {'exclude_offline': exclude_offline}
        response = await self.request('GET',
                                      f'servers/{server_id}/members',
                                      json=data)
        return response

    async def fetch_user(self, user_id: str):
        """
        Fetch a user you can see.

        Args:
            self: Represent the instance of the class
            user_id: str: Specify the user_id of the user you want to fetch

        Returns:
            The user's data
        """
        return await self.request('GET', f'users/{user_id}')

    async def fetch_member(self, server_id: str, user_id: str):
        """
        Fetch a single member from a server you're part of.

        Args:
            self: Represent the instance of the class
            server_id: str: Specify the server id of the server you want to fetch a member from
            user_id: str: Fetch a member by their user id
        """
        return await self.request('GET', f'servers/{server_id}/members/{user_id}')

    async def edit_user(self,
                        user_id: str,
                        display_name: str = None,
                        # avatar: str = None,
                        status: models.Status = None,
                        profile: models.UserProfile = None,
                        # badges: int = None,
                        # flags: int = None,
                        remove: List[UserRemove] = None
                        ):
        """
        Edit a user currently authorized.

        Args:
            self: Represent the instance of the class
            user_id: str: Specify the id of a user you want to edit
            display_name: str: Set the display name of a user
            status: Status: Set the user's status
            profile: UserProfile: Set the user's profile
            remove: List[UserRemove]: Remove the user's "Avatar", "StatusText", "StatusPresence", "ProfileContent", "ProfileBackground", "DisplayName"

        Returns:
            A dict
        """

        json = {
            'display_name': None,
            'status': None,
            'profile': None,
            'remove': remove
        }
        if display_name:
            validate_display_name(display_name)
            json['display_name'] = display_name
        # if avatar:
        #     if len(avatar) > 128 or len(avatar) < 1:
        #         raise ValueError(
        #             "Avatar url can be min 1 character or max 128 characters")
        #     json["avatar"] = avatar
        if status:
            json["status"] = status.to_dict()
        if profile:
            json["profile"] = profile.to_dict()
        return await self.request("PATCH", f'users/{user_id}', json=json)

    async def fetch_user_flags(self, user_id: str):
        """
        Fetch the flags for a user you can see.

        Args:
            self: Represent the instance of the class
            user_id: str: the user id
        """
        return await self.request("GET", f"users/{user_id}/flags")

    async def fetch_user_profile(self, user_id: str):
        """
        Fetch profile of a user you can see.

        Args:
            self: Access the class attributes and methods
            user_id: str: Specify the user id of the profile you want to retrieve
        """
        return await self.request("GET", f"users/{user_id}/profile")

    async def fetch_dm_channels(self):
        """
        Fetch all DM channels.

        Args:
            self: Represent the instance of the class
        """
        return await self.request("GET", f"users/dms")

    async def create_dm_channel(self, user_id: str):
        """
        Create a DM channel with a user.

        Args:
            self: Represent the instance of the class
            user_id: str: Identify the user that you want to create a dm channel with

        Returns:
            A channel object dict
        """
        return await self.request("GET", f"users/{user_id}/dm")

    async def fetch_channel(self, channel_id: str):
        """
        Fetch a channel from a server you're in.

        Args:
            self: Represent the instance of the class
            channel_id: str: Specify the channel id of the channel you want to fetch
        """
        return await self.request('GET', f'channels/{channel_id}')

    async def close_channel(self, channel_id: str):
        """
        The close_channel function closes a channel.

        Args:
            self: Represent the instance of the class
            channel_id: str: Identify the channel to be closed
        """
        return await self.request('DELETE', f'channels/{channel_id}')

    delete_channel = close_channel

    async def edit_channel(self,
                           channel_id: str,
                           name: str = None,
                           description: str = None,
                           #    icon: str = None,
                           nsfw: bool = False,
                           archived: bool = False,
                           remove: List[ChannelRemove] = None
                           ):
        """
        Edit a server channel.

        Args:
            self: Represent the instance of the class
            channel_id: str: Specify the channel to edit
            name: str: Set the name of the channel
            description: str: Set the channel description
            nsfw: bool: Set the channel to nsfw or not
            archived: bool: Archive the channel
            remove: ChannelRemove: List of enums/strings for stuff you want to remove: "Description", "Icon", "DefaultPermissions"

        Returns:
            A raw event dict
        """

        json = {'name': None, 'description': None, "icon": None,
                'nsfw': nsfw, 'archived': archived, 'remove': remove}
        if name:
            if len(name) > 32 or len(name) < 1:
                raise ValueError(
                    "Chanel name can be min 1 and max 32 characters")
            json['name'] = name
        if description:
            if len(description) > 1024 or len(description) < 1:
                raise ValueError(
                    "Chanel description can be min 1 and max 1024 characters")
            json['description'] = description
        # if icon:
        #     if len(icon) > 128 or len(icon) < 1:
        #         raise ValueError(
        #             "Chanel icon id can be min 1 and max 128 characters")
        #     json['icon'] = icon
        return await self.request('PATCH', f'chanels/{channel_id}', json=json)

    async def create_invite(self, channel_id: str):
        """Create an invite for a TextChannel"""
        return await self.request("POST", f"channels/{channel_id}/invites")

    async def set_channel_role_permissions(self, channel_id: str, role_id: str, allow: List[Permissions] = None, deny: List[Permissions] = None):
        """
        Set role permissions for a TextChannel or a VoiceChannel

        Args:
            self: Represent the instance of the class
            channel_id: str: Specify the channel you want to set permissions for
            role_id:str: Set the role id for which you want to change permissions
            allow: List[Permissions]: Set the permissions for a role in a channel
            deny: List[Permissions]: Deny permissions to a role
        """
        json = {'permissions': {
            'allow': Permissions.set_permissions(allow),
            'deny': Permissions.set_permissions(deny)
        }}
        return await self.request("PUT", f"chanels/{channel_id}/permissions/{role_id}", json=json)

    async def set_default_permissions(self, channel_id: str, allow: List[Permissions] = None, deny: List[Permissions] = None):
        """
        Set default role permissions for a TextChannel or a VoiceChannel

        Args:
            self: Represent the instance of the class
            channel_id: str: Specify the channel you want to set permissions for
            allow: List[Permissions]: Set the permissions for a role in a channel
            deny: List[Permissions]: Deny permissions to a role
        """
        json = {'permissions': {
            'allow': Permissions.set_permissions(allow),
            'deny': Permissions.set_permissions(deny)
        }}
        return await self.request("PUT", f"chanels/{channel_id}/permissions/default", json=json)

    async def fetch_messages(self,
                             channel_id: str,
                             limit: int = 100,
                             before: str = None,
                             after: str = None,
                             sort: MessageSort = 'Latest',
                             nearby: str = None,
                             include_users: bool = True
                             ):
        """
        Fetch messages from a chanel

        Args:
            self: Represent the instance of the class
            channel_id: str: Specify which channel to fetch messages from
            limit: int: Maximum number of messages to fetch. For fetching nearby messages, this is `(limit + 1)`.
            before: str: Message id before which messages should be fetched
            after: str: Message id after which messages should be fetched
            sort: MessageSort: Message sort direction. Enum: "Relevance" "Latest" "Oldest" 
            nearby: str: Message id to search around. Specifying 'nearby' ignores 'before', 'after' and 'sort'. It will also take half of limit rounded as the limits to each side. It also fetches the message ID specified.
            include_users: bool: Whether to include user (and member, if server channel) objects
        """
        json = {
            "limit": None,
            'before': None,
            'after': None,
            'sort': sort,
            "nearby": None,
            'include_users': include_users
        }
        if limit:
            if len(limit) > 100 or len(limit) < 1:
                raise ValueError("You can fetch min 1 and max 100 messages")
            json['limit'] = limit
        if before:
            json["before"] = before
        if after:
            json["after"] = after
        if nearby:
            json["nearby"] = nearby

        return await self.request("GET", f'channels/{channel_id}/messages', json=json)

    async def upload_file(self, file: models.UploadableFile, tag: Literal["attachments", "avatars", "backgrounds", "icons", "banners", "emojis"] = 'attachments', spoiler: bool = False):
        url = f'https://autumn.revolt.chat/{tag}'
        headers = {
            "User-Agent": "Pyre"
        }
        f = file.open_file()
        if spoiler:
            fn = f'SPOILER_{file.file_name}'
        else:
            fn = file.file_name
        files = {'upload-file': (fn, f)}

        resp = await self.session.post(url, files=files, headers=headers)
        resp_json = resp.json()

        resp_code = resp.status_code

        if resp_code == 400:
            raise HTTPError(resp_json)
        elif 500 <= resp_code <= 600:
            raise InternalError(resp_json)
        else:
            return {'id': resp_json["id"], "url": f'{url}/{resp_json["id"]}'}

    async def send_message(self,
                           channel_id: str,
                           content: str = None,
                           attachments: List[models.UPLOADABLE_TYPE] = None,
                           replies: List[models.Reply] = None,
                           embeds: List[models.Embed] = None,
                           masquerade: models.Masquerade = None,
                           interactions: models.Interactions = None,
                           spoiler_attachments: bool = False,
                           ):
        url = f'channels/{channel_id}/messages'
        headers = {'Idempotency-Key': random_string_generator()}
        json = {}
        if content:
            if len(content) > 2000:
                raise ValueError("Message content can be max 2000 characters")
            json["content"] = content
        if attachments:
            if len(attachments) > 10:
                raise ValueError("There can be max 10 attachments per message")
            atts = []
            for a in attachments:
                if isinstance(a, models.UploadableFile):
                    attfile = a
                else:
                    attfile = models.UploadableFile(file=a)
                att_id = await self.upload_file(attfile, spoiler=spoiler_attachments)
                atts.append(att_id['id'])
            json["attachments"] = atts
        if replies:
            json['replies'] = [r.to_dict() for r in replies]
        if embeds:
            if len(embeds) > 10:
                raise ValueError("There can be max 10 embeds per message")
            embed_dicts = []
            for embed in embeds:
                if embed.media:
                    if isinstance(embed.media, models.UploadableFile):
                        medfile = embed.media
                    else:
                        medfile = models.UploadableFile(file=embed.media)
                    med_id = await self.upload_file(medfile)
                    embed.media = med_id['id']
                    embed_dict = embed.model_dump()
                    embed_dict['type'] = 'Text'
                    embed_dicts.append(embed_dict)
            json['embeds'] = embed_dicts
        if interactions:
            json["interactions"] = interactions.to_dict()
        if masquerade:
            json["masquerade"] = masquerade.to_dict()
        return await self.request('POST', url, extra_headers=headers, json=json)

    async def reply(self,
                    channel_id: str,
                    message_id: str,
                    content: str = None,
                    attachments: List[models.UPLOADABLE_TYPE] = [],
                    file: models.UPLOADABLE_TYPE = None,
                    embeds: List[models.Embed] = [],
                    embed: models.Embed = None,
                    masquerade: models.Masquerade = None,
                    interactions: models.Interactions = None,
                    spoiler_attachments: bool = False,
                    mention: bool = False):
        if embed:
            embeds.append(embed)
        if file:
            attachments.append(file)
        return await self.send_message(
            channel_id=channel_id,
            content=content,
            attachments=attachments,
            embeds=embeds,
            masquerade=masquerade,
            interactions=interactions,
            spoiler_attachments=spoiler_attachments,
            replies=[models.Reply(id=message_id, mention=mention)])

    async def search_messages(self, channel_id: str, query: str, limit: int = None, before: str = None, after: str = None, sort: Literal['Relevance', 'Latest', 'Oldest'] = 'Latest', include_users: bool = False):
        """
        This route searches for messages within the given parameters.

        Args:
            self: Represent the instance of the class
            channel_id: str: Specify the channel to search in
            query: str: Full-text search query. See MongoDB documentation for more information.
            limit: int: [ 1 .. 100 ] Maximum number of messages to fetch
            before: str: Message id before which messages should be fetched
            after: str: Message id after which messages should be fetched
            sort: str:  Default: "Relevance" Enum: "Relevance" "Latest" "Oldest". Sort used for retrieving messages
            include_users: bool: Whether to include user (and member, if server channel) objects
        """

        json = {}
        if len(query) > 64 or len(query) < 1:
            raise ValueError("query can have min 1 and max 64 characters")
        if limit:
            if limit > 100 or limit < 1:
                raise ValueError("limit can be int he range of 1 to 100")
            json["limit"] = limit
        if before:
            if len(before) != 26:
                raise ValueError("incorrect before id")
            json['before'] = before
        if after:
            if len(after) != 26:
                raise ValueError("incorrect after id")
            json['after'] = after
        json["sort"] = sort
        json['include_users'] = include_users
        return await self.request('POST', f'channels/{channel_id}/search', json=json)

    async def fetch_message(self, channel_id: str, message_id: str):
        """Retrieves a message by its id."""
        return await self.request("GET", f"channels/{channel_id}/messages/{message_id}")

    async def delete_message(self, channel_id: str, message_id: str):
        """Delete a message you've sent or one you have permission to delete."""
        return await self.request('DELETE', f"channels/{channel_id}/messages/{message_id}")

    async def edit_message(self, channel_id: str, message_id: str, content: str = None, embeds: List[models.Embed] = [], embed: models.Embed = None):
        """
        Edits a message that you've previously sent.

        Args:
            self: Represent the instance of the class
            channel_id: str: Specify the channel in which to send the message
            message_id:str: Specify which message to edit
            content: str: Set the content of the message. Max 2000 characters.
            embeds: List[models.Embed]: Add embeds to the message. Max 10 embeds.
            embed:models.Embed: Add an embed to the message. Counts together with embeds.
        """
        if embed:
            embeds.append(embed)
        if embeds:
            if len(embeds) > 10:
                raise ValueError("There can be max 10 embeds per message")
            embed_dicts = []
            for embed in embeds:
                if embed.media:
                    if isinstance(embed.media, models.UploadableFile):
                        medfile = embed.media
                    else:
                        medfile = models.UploadableFile(file=embed.media)
                    med_id = await self.upload_file(medfile)
                    embed.media = med_id['id']
                    embed_dict = embed.model_dump()
                    embed_dict['type'] = 'Text'
                    embed_dicts.append(embed_dict)
        if len(content) > 2000:
            raise ValueError("Message content can have max 2000 characters.")
        return await self.request('PATCH', f"channels/{channel_id}/messages/{message_id}", json={'content': content, 'embeds': embed_dicts})

    async def bulk_delete_messages(self, channel_id: str, ids: List[str]):
        """
        Delete multiple messages you've sent or one you have permission to delete.

        This will always require `ManageMessages` permission regardless of whether you own the message or not.

        Messages must have been sent within the past 1 week.

        """
        if len(ids) > 100 or len(ids) < 1:
            raise ValueError(
                "There has to be at least 1 message id or max 100 message ids")
        return await self.request('DELETE', f'channels/{channel_id}/messages/bulk', json={'ids': ids})

    async def add_reaction(self, channel_id: str, message_id: str, emoji: str):
        return await self.request("PUT", f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}")

    async def remove_reaction(self, channel_id: str, message_id: str, emoji: str, user_id: str = None, remove_all: bool = False):
        """
        Remove your own, someone else's or all of a given reaction.

        Requires `ManageMessages` if changing others' reactions.

        """
        url = f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}"
        if user_id:
            url += f'?user_id={user_id}'
        if remove_all:
            url += f"?remove_all=true"

        return await self.request("DELETE", url)

    async def remove_reactions(self, channel_id: str, message_id: str):
        """
        Remove all reactions on a given message.

        Requires `ManageMessages` permission.
        """
        return await self.request("DELETE", f"channels/{channel_id}/messages/{message_id}/reactions")

    async def fetch_group_members(self, group_id: str):
        """Retrieves all users who are part of this group."""
        return await self.request("GET", f"channels/{group_id}/members")

    async def create_group(self, name: str, users: List[str], description: str = None, nsfw: bool = False):
        json = {
            'nsfw': nsfw
        }
        if len(name) > 32:
            raise ValueError("Group name can have max 32 characters.")
        json['name'] = name
        if len(users) > 49:
            raise ValueError("Group can have max 49 users")
        json['users'] = users
        if description:
            if len(description) > 1024:
                raise ValueError(
                    "Group description can have max 1024 characters")
            json['description'] = description

        return await self.request("POST", f"channels/create", json=json)

    async def add_member_to_group(self, group_id: str, member_id: str):
        """Adds another user to the group."""
        return await self.request("PUT", f"channels/{group_id}/recipients/{member_id}")

    async def remove_member_from_group(self, group_id: str, member_id: str):
        """Removes a user from the group."""
        return await self.request("DELETE", f"channels/{group_id}/recipients/{member_id}")

    async def fetch_server(self, server_id: str, include_channels: bool = False):
        """Fetch a server by its id"""
        url = f"servers/{server_id}"
        if include_channels:
            url += '?include_channels=true'
        return self.request("GET", url)

    async def leave_server(self, server_id: str, leave_silently: bool = False):
        """Deletes a server if owner otherwise leaves."""
        url = f"servers/{server_id}"
        if leave_silently:
            url += '?leave_silently=true'
        return self.request("GET", url)

    async def create_channel(self, server_id: str, name: str, description: str = None, type: Literal['Text', 'Voice'] = 'Text', nsfw: bool = False):
        """Create a new Text or Voice channel."""
        json = {'nsfw': nsfw}
        if type != 'Text' or type != "Voice":
            raise ValueError("Channels can be either 'Text' or 'Voice'")
        json['type'] = type
        if len(name) > 32 or len(name) < 1:
            raise ValueError(
                "Channel name has to ahve at least 1 character and max 32 characters")
        json['name'] = name
        if description:
            if len(description) > 1024:
                raise ValueError(
                    "Channel description can have max 1024 characters")
            json['description'] = description
        return await self.request("POST", f"servers/{server_id}/channels", json=json)

    async def kick_member(self, server_id: str, member_id: str):
        """Kick a member from the server."""
        return await self.request('DELETE', f"servers/{server_id}/members/{member_id}")

    async def edit_member(self, server_id: str, member_id: str, nickname: str = None, roles: List[str] = None, timeout: datetime = None, remove: Literal['Nickname', 'Avatar', 'Roles', 'Timeout'] = None):
        """Edit a member by their id."""
        data = {}
        if nickname:
            if len(nickname) > 32:
                raise ValueError('Nickname can have max 32 characters')
            data["nickname"] = nickname
        if roles:
            data['roles'] = roles
        if timeout:
            data["timeout"] = timeout
        if remove:
            data["remove"] = remove
        return await self.request("PATCH", f'servers/{server_id}/members/{member_id}', json=data)

    async def ban_user(self, server_id: str, user_id: str, reason: str = None):
        """Ban member user by their id"""
        data = {}
        if reason:
            if len(reason) > 1024 or len(reason) < 1:
                raise ValueError("Reason can be min 1 and max 1024 characters")
            data['reason'] = reason

        return await self.request("PUT", f'servers/{server_id}/bans/{user_id}')

    async def unban_user(self, server_id: str, user_id: str, reason: str = None):
        """Unban member user by their id"""
        data = {}
        if reason:
            if len(reason) > 1024 or len(reason) < 1:
                raise ValueError("Reason can be min 1 and max 1024 characters")
            data['reason'] = reason

        return await self.request("DELETE", f'servers/{server_id}/bans/{user_id}')

    async def fetch_bans(self, server_id: str):
        """Fetch all bans on a server."""
        return await self.request("GET", f"server/{server_id}/bans")

    async def fetch_invites(self, server_id: str):
        """Fetch all invites on a server."""
        return await self.request('GET', f'servers/{server_id}/invites')

    async def create_role(self, server_id: str, name: str, rank: int = None):
        """Creates a new server role"""
        data = {}
        if len(name) > 32:
            raise ValueError("Role name can have max 32 characters")
        data['name'] = name
        if rank:
            data["rank"] = rank
        return await self.request('POST', f'servers/{server_id}/roles', json=data)

    async def delete_role(self, server_id: str, role_id: str):
        """Delete a role in the server"""
        return await self.request('DELETE', f'servers/{server_id}/roles/{role_id}')

    async def edit_role(self, server_id: str, role_id: str, name: str = None, rank: int = None, colour: str = None, show_separetely: bool = False, remove: Literal['Colour'] = None):
        """Edit a role by its id"""
        data = {}
        if len(name) > 32:
            raise ValueError("Role name can have max 32 characters")
        data['name'] = name
        if rank:
            data["rank"] = rank
        if colour:
            if validate_colour(colour):
                data['colour'] = colour
        if show_separetely:
            data["show_separately"] = True
        if remove:
            data["remove"] = remove
        return await self.request('PATCH', f'servers/{server_id}/roles/{role_id}', json=data)

    async def set_role_permissions(self, server_id: str, role_id: str, allow: List[Permissions]=None, deny:List[Permissions]=None):
        """Sets permissions for the specified role in the server."""
        json = {'permissions': {
            'allow': Permissions.set_permissions(allow),
            'deny': Permissions.set_permissions(deny)
        }}
        return await self.request("PUT", f'servers/{server_id}/permissions/{role_id}',json=json)
    
    async def set_default_role_permissions(self, server_id:str, allow: List[Permissions]=None, deny:List[Permissions]=None):
        json = {'permissions': {
            'allow': Permissions.set_permissions(allow),
            'deny': Permissions.set_permissions(deny)
        }}
        return await self.request("PUT", f'servers/{server_id}/permissions/default',json=json)
    
    async def create_webhook(self, channel_id: str, name:str, description:str=None):
        """Creates a webhook which 3rd party platforms can use to send messages"""
        data = {}
        if len(name) > 32:
            raise ValueError("Webhook name can have max 32 characters")
        data['name'] = name
        if description:
            if len(description) > 128:
                raise ValueError("Webhook description can have max 128 characters")
            data['description'] = description
        return await self.request('POST', f'channels/{channel_id}/webhooks')
    
    async def fetch_all_webhooks(self, channel_id: str):
        """Fetches all webhooks in a channel"""
        return await self.request('GET', f'channels/{channel_id}/webhooks')


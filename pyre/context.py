from .models import BaseCommand, PyreObject, Server, Member, TextMessage, TextChannel

class BaseContext(PyreObject):
    command: BaseCommand
    author_id: str
    channel_id: str
    message_id: str
    server_id:str

    @property
    def server(self) -> Server:
        return self.client.cache.get_server(self.server_id)
    
    @property
    def author(self) -> Member:
        return self.client.cache.get_member(self.author_id)
    
    @property
    def message(self) -> TextMessage:
        return self.client.cache.get_message(self.message_id)
    
    @property
    def channel(self) -> TextChannel:
        return self.client.cache.get_channel(self.channel_id)



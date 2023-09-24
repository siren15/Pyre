from typing import Dict, Literal, Optional, Any, List, Union
from pydantic import ConfigDict, Field as field, BaseModel
from .base import PyreObject
from .file import File, UPLOADABLE_TYPE


class EmbedImage(PyreObject):
    url: str
    width: int
    height: int
    size: str


class EmbedVideo(PyreObject):
    url: str
    width: int
    height: int


class WebsiteEmbed(PyreObject):
    type: str = 'Website'
    url: Optional[str] = None
    original_url: Optional[str] = None
    special: Optional[Any] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[EmbedImage] = None
    video: Optional[EmbedVideo] = None
    site_name: Optional[str] = None
    icon_url: Optional[str] = None
    colour: Optional[str] = field(pattern='(?i)^(?:[a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|(repeating-)?(linear|conic|radial)-gradient\(([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|\d+deg)([ ]+(\d{1,3}%|0))?(,[ ]*([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+)([ ]+(\d{1,3}%|0))?)+\))$', default=None)


class ImageEmbed(EmbedImage):
    type: str = 'Image'


class VideoEmbed(EmbedVideo):
    type: str = 'Video'


class RevoltEmbed(PyreObject):
    type: str = 'Text'
    icon_url: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    media: Optional[File] = None
    colour: Optional[str] = field(pattern='(?i)^(?:[a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|(repeating-)?(linear|conic|radial)-gradient\(([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|\d+deg)([ ]+(\d{1,3}%|0))?(,[ ]*([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+)([ ]+(\d{1,3}%|0))?)+\))$', default=None)

class EmbedField(BaseModel):
    name: str = None
    content: str = None
    inline: bool = True

class Embed(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """A sendable embed model, that can be sent in messages, you will never receive this, you will receive :class:`RevoltEmbed`."""
    icon_url: Optional[str] = field(default=None, max_length=128)
    """URL of the icon"""
    url: Optional[str] = field(default=None, max_length=256)
    """URL for hyperlinking the embed's title"""
    title: Optional[str] = field(default=None, max_length=100)
    """Title of the embed"""
    description: Optional[str] = field(default=None, max_length=2000)
    """Desfription of the embed"""
    media: Optional[UPLOADABLE_TYPE] = None
    """The file inside the embed, this will be automatically uploaded when sending a message."""
    colour: Optional[str] = field(pattern='(?i)^(?:[a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|(repeating-)?(linear|conic|radial)-gradient\(([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|\d+deg)([ ]+(\d{1,3}%|0))?(,[ ]*([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+)([ ]+(\d{1,3}%|0))?)+\))$', default=None)
    """The embed's accent colour, this is any valid `CSS color <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>`_"""

class NullEmbed(PyreObject):
    type: str = 'None'


EMBEDS = Union[
    WebsiteEmbed,
    ImageEmbed,
    VideoEmbed,
    RevoltEmbed,
    NullEmbed
]

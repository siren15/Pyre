from .base import PyreEvent


class ClientReady(PyreEvent):
    """Used to register when the client is actually ready."""


class ClientError(PyreEvent):
    """Used to register error events"""

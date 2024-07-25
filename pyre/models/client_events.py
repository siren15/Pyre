from .base import PyreEvent

class Ready(PyreEvent):
    """Used to register when the client is actually ready."""

class ClientReady(PyreEvent):
    """Used to register when the client is actually ready."""


class ClientError(PyreEvent):
    """Used to register error events"""


CLIENT_ERRORS = ClientError | ClientReady | Ready

CL_ERRS = [
    ClientReady,
    ClientError,
    Ready
]
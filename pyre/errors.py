class PyreError(Exception):
    """Main lib exception"""


class LabelMe(PyreError):
    """Uncategorized error"""


class InternalError(PyreError):
    """The server ran into an issue"""


class InvalidSession(PyreError):
    """Authentication details are incorrect"""


class OnboardingNotFinished(PyreError):
    """User has not chosen a username"""


class AlreadyAuthenticated(PyreError):
    """This connection is already authenticated"""


class InvalidDisplayName(PyreError):
    """Display name is invalid"""


class HTTPError(PyreError):
    """HTTP Error"""


class PermissionError(PyreError):
    """User does not have the required permissions"""


class ValidationError(PyreError):
    """User input is invalid"""

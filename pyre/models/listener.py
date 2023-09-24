import attrs
from typing import Any
import re

def to_snake_case(model_name):
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', model_name).lower()
    return f"on_{snake_case}"


def to_pascal_case(snake_case):
    without_prefix = re.sub(r'^on_', '', snake_case)
    pascal_case = re.sub(r'(?:^|_)([a-z])', lambda m: m.group(1).upper(),
                         without_prefix)
    return pascal_case


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Listener:
    """
    A listener object for events.
    """
    name: str = attrs.field(repr=False)
    """The name of the event.""" ""
    event: Any = attrs.field(repr=False)
    """The event object."""
    callback: callable = attrs.field(repr=False)
    """The callback function."""

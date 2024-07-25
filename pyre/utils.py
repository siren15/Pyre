import random
import re
from typing import Dict
from .errors import InvalidDisplayName


def validate_display_name(name: str):
    regex_pattern = r'^[^\u200B\n\r]+$'
    if not re.match(regex_pattern, name):
        raise InvalidDisplayName(
            'Display name does not match this regex ^[^\u200B\n\r]+$')

    if len(name) < 2 or len(name) > 32:
        raise InvalidDisplayName(
            'Display name cannot have less than 2 or more than 32 characters')

    return True

def validate_colour(colour: str):
    regx = r'(?i)^(?:[a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|(repeating-)?(linear|conic|radial)-gradient\(([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+|\d+deg)([ ]+(\d{1,3}%|0))?(,[ ]*([a-z ]+|var\(--[a-z\d-]+\)|rgba?\([\d, ]+\)|#[a-f0-9]+)([ ]+(\d{1,3}%|0))?)+\))$'
    if not re.match(regx, colour):
        raise ValueError("Invalid colour pattern")
    return True

def delete_key(dict_key:str, d: Dict):
    """Delete any instance of key from dictionary, and it's nested dictionaries"""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == dict_key:
                del d[key]
            elif isinstance(d[key], dict):
                delete_key(dict_key, d[key])
    return d

def random_string_generator(r: int = 8):
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    result=''
    for i in range(0, r):
        result += random.choice(characters)
    return result

def correct_event_name_formatting(event_name:str):
    event_name = event_name.removeprefix('on_').removesuffix('_')
    if '_' in event_name:
        return ''.join(word.capitalize() for word in event_name.split('_'))
    else:
        return event_name.capitalize()
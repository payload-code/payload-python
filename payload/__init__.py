"""
Payload python library
------------------------

Documentation: https://docs.payload.com

:copyright: (c) 2021 Payload (http://payload.com)
:license: MIT License
"""

from .version import __version__
from .exceptions import *
from .objects import *
from .arm import Attr as attr, ARMRequest, session_factory
from . import objects

URL = 'https://api.payload.com'

api_key = None
api_url = URL

Session = session_factory('PayloadSession', objects)


def create(*args, **kwargs):
    return ARMRequest().create(*args, **kwargs)


def update(*args, **kwargs):
    return ARMRequest().update(*args, **kwargs)


def delete(*args, **kwargs):
    return ARMRequest().delete(*args, **kwargs)

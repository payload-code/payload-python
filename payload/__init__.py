"""
Payload python library
------------------------

Documentation: https://docs.payload.co

:copyright: (c) 2019 Payload (http://payload.co)
:license: MIT License
"""

from .version import __version__
from .exceptions import *
from .objects import *
from .arm import Attr as attr, ARMRequest

URL = 'https://api.payload.co'

api_key = None
api_url = URL

def create(*args, **kwargs):
	return ARMRequest().create(*args, **kwargs)

def update(*args, **kwargs):
	return ARMRequest().update(*args, **kwargs)

def delete(*args, **kwargs):
	return ARMRequest().delete(*args, **kwargs)

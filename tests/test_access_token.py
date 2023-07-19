import random
import string

import pytest

import dateutil.parser

import payload as pl
from payload.exceptions import NotFound

from .fixtures import Fixtures


class TestAccessToken(Fixtures):
    def test_create_client_key(self, api_key):
        client_key = pl.ClientKey.create()
        assert client_key.status == "active"
        assert client_key.type == "client"
        assert client_key.environ == 'test'
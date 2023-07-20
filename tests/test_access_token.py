import random
import string

import pytest

import dateutil.parser

import payload as pl
from payload.exceptions import NotFound

from .fixtures import Fixtures


class TestAccessToken(Fixtures):
    def test_create_client_token(self, api_key):
        client_token = pl.ClientKey.create()
        assert client_token.status == "active"
        assert client_token.type == "client"
        assert client_token.environ == 'test'

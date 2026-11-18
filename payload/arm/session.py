import payload

from . import Attr
from .object import ARMObjectWrapper
from .request import ARMRequest


def get_object(objects, name):
    if isinstance(objects, dict):
        return objects[name]
    else:
        return getattr(objects, name)


class Session(object):
    attr = Attr

    def __init__(self, api_key=None, api_url=None, api_version=None):
        self.api_key = api_key or payload.api_key
        self.api_url = api_url or payload.api_url
        self.api_version = api_version or payload.api_version

    def create(self, *args, idempotency_key=None, **kwargs):
        headers = {'Idempotency-Key': idempotency_key} if idempotency_key else None
        return ARMRequest(session=self).create(*args, _headers=headers, **kwargs)

    def update(self, *args, **kwargs):
        return ARMRequest(session=self).update(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return ARMRequest(session=self).delete(*args, **kwargs)

    def __getattr__(self, name):
        return ARMObjectWrapper(get_object(self._objects, name), self)


def session_factory(name, objects):
    return type(name, (Session,), {'_objects': objects})

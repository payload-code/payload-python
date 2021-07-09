from .request import ARMRequest
from .object import ARMObject, ARMObjectWrapper
import types
import inspect
import payload

def get_object(objects, name):
    if isinstance(objects, dict):
        return objects[name]
    else:
        return getattr(objects, name)

class Session(object):
    def __init__(self, api_key=None, api_url=None):
        self.api_key = api_key or payload.api_key
        self.api_url = api_url or payload.api_url

    def create(self, *args, **kwargs):
        return ARMRequest(session=self).create(*args, **kwargs)

    def update(self, *args, **kwargs):
        return ARMRequest(session=self).update(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return ARMRequest(session=self).delete(*args, **kwargs)

    def __getattr__(self, name):
        return ARMObjectWrapper(get_object(self._objects, name), self)

def session_factory(name, objects):
    return type(name, (Session,), {'_objects': objects})

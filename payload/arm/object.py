from .attr import MetaAttr
from functools import partial
from six import with_metaclass
import json

_object_cache = {}

class ARMMetaObject(MetaAttr):
    def __new__(cls, name, bases, dct):
        if len(bases) and hasattr( bases[0], '__spec__' ):
            dct['__spec__'] = dict(bases[0].__spec__, **dct['__spec__'])

        self = super(ARMMetaObject, cls).__new__(cls, name, bases, dct)

        if len(bases):
            _object_cache[self] = {}
            if 'endpoint' not in self.__spec__:
                self.__spec__['endpoint'] = '/{}s'.format(self.__spec__['object'])

        return self

class ARMObject(with_metaclass(ARMMetaObject)):
    __spec__ = {}
    _session = None
    field_map = set()

    def __new__(cls, _session=None, **obj):
        if 'id' in obj:
            uid = obj['id']
            if uid in _object_cache[cls]:
                _object_cache[cls][uid]._set_data(obj)
                return _object_cache[cls][uid]
        return super(ARMObject, cls).__new__(cls)

    def __init__(self, _session=None, **obj):
        self._session = _session
        self._set_data(dict(self.__spec__.get('polymorphic') or {}, **obj))

    def __getattr__(self, attr):
        if attr in self.field_map:
            return self._data.get(self._data.get('type'),{}).get(attr)
        return self._data.get(attr)

    def _set_data(self, obj):
        self._data = obj
        self._data = data2object(self._data, self.field_map, self._session)
        if 'id' in obj:
            _object_cache[self.__class__][obj['id']] = self

    def json(self):
        return json.dumps( self.data(), indent=4, sort_keys=True )

    def data(self):
        return object2data(self._data)

    def update(self, **update):
        ARMRequest(self.__class__, self._session)._request('put', id=self.id, json=update)

    def delete(self):
        ARMRequest(self.__class__, self._session)._request('delete', id=self.id)

    @classmethod
    def get(cls, id, *args, **kwargs):
        return ARMRequest(cls, kwargs.pop('_session', None)).get(id, *args, **kwargs)

    @classmethod
    def filter_by(cls, *filters, **kw_filters):
        return ARMRequest(cls, kw_filters.pop('_session', None))\
            .filter_by(*filters, **dict(cls.__spec__.get('polymorphic') or {}, **kw_filters))

    @classmethod
    def create(cls, objects=None, **values):
        return ARMRequest(cls, values.pop('_session', None))\
            .create(objects, **values)

    @classmethod
    def select(cls, *fields, _session=None):
        return ARMRequest(cls, _session).select(*fields)\
            .filter_by(**dict(cls.__spec__.get('polymorphic') or {}))

    @classmethod
    def update_all(cls, objects=None, **values):
        return ARMRequest(cls, values.pop('_session', None))\
            .update(objects, **values)

    @classmethod
    def delete_all(cls, objects=None, **values):
        return ARMRequest(cls, values.pop('_session', None))\
            .delete(objects, **values)

class ARMMetaObjectWrapper(object):
    def __getattr__(cls, key):
        if key == 'Foo':
            return cls._foo_func()
        elif key == 'Bar':
            return cls._bar_func()
        raise AttributeError(key)

class ARMObjectWrapper(object):
    def __init__(self, Object, session):
        self.Object = Object
        self.session = session

    def __call__(self, *args, **kwargs):
        obj = self.Object(*args, **kwargs)
        obj._session = self.session
        return obj

    def call(self, __name, *args, **kwargs):
        kwargs['_session'] = self.session
        return getattr(self.Object, __name)(*args, **kwargs)

    def __getattr__(self, name):
        if name in ('get', 'filter_by', 'create', 'select', 'update_all', 'delete_all'):
            return partial(self.call, name)

        return getattr(self.Object, name)


from .request import ARMRequest
from ..utils import object2data, data2object

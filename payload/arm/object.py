from .attr import MetaAttr
from six import with_metaclass

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
    field_map = None

    def __new__(cls, **obj):
        if 'id' in obj:
            uid = obj['id']
            if uid in _object_cache[cls]:
                _object_cache[cls][uid]._set_data(obj)
                return _object_cache[cls][uid]
        return super(ARMObject, cls).__new__(cls)

    def __init__(self, **obj):
        self._set_data(dict(self.__spec__.get('polymorphic') or {}, **obj))

    def __getattr__(self, attr):
        return self._data.get(attr)

    def _set_data(self, obj):
        self._data = obj
        self._data = data2object(self._data)
        if 'id' in obj:
            _object_cache[self.__class__][obj['id']] = self

    def json(self):
        return json.dumps( self.data(), indent=4, sort_keys=True )

    def data(self):
        return object2data(self._data)

    def update(self, **update):
        ARMRequest(self.__class__)._request('put', id=self.id, json=update)

    def delete(self):
        ARMRequest(self.__class__)._request('delete', id=self.id)

    @classmethod
    def get(cls, id, *args, **kwargs):
        return ARMRequest(cls).get(id, *args, **kwargs)

    @classmethod
    def filter_by(cls, *filters, **kw_filters):
        return ARMRequest(cls)\
            .filter_by(*filters, **dict(cls.__spec__.get('polymorphic') or {},**kw_filters))

    @classmethod
    def create(cls, objects=None, **values):
        return ARMRequest(cls)\
            .create(objects, **values)

    @classmethod
    def select(cls, *fields):
        return ARMRequest(cls).select(*fields)\
            .filter_by(**dict(cls.__spec__.get('polymorphic') or {}))

    @classmethod
    def update_all(cls, objects=None, **values):
        return ARMRequest(cls)\
            .update(objects, **values)

    @classmethod
    def delete_all(cls, objects=None, **values):
        return ARMRequest(cls)\
            .delete(objects, **values)

from .request import ARMRequest
from ..utils import object2data

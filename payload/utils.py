from .arm.object import ARMObject, _object_cache
from .arm.attr import Attr

def get_object_cls(item):
    cls = None
    for Object in _object_cache:
        if Object.__spec__['object'] != item['object']:
            continue
        if 'polymorphic' in Object.__spec__:
            found = True
            for attr, val in Object.__spec__['polymorphic'].items():
                if item.get(attr) != val:
                    found = False
                    break
            if found:
                cls = Object
                break
        elif not cls:
            cls = Object
    return cls

def map_object(item):
    cls = get_object_cls(item)
    if cls:
        return cls(**item)
    return item

def nested_qstring_keys(base):
    def recurse(item, fmt='{}'):
        if isinstance( item, (list,tuple) ):
            _iter = enumerate(item)
        else:
            _iter = list(item.items())
        for key, val in _iter:
            new_key = fmt.format(key)
            if not isinstance(item[key], (dict, list, tuple)):
                if isinstance(val, Attr):
                    val = str(Attr)
                base[new_key] = val
            else:
                if item is base: del base[key]
                recurse(val, new_key+'[{}]')
        return base
    return recurse(base)

def data2object(item):
    def recurse(item):
        if isinstance( item, (list,tuple) ):
            _iter = enumerate(item)
        else:
            _iter = list(item.items())
        for key, val in _iter:
            if isinstance(val, (list, dict)):
                item[key] = recurse(val)
            if isinstance(val, dict)\
            and val.get('object'):
                Object = get_object_cls(val)
                if Object:
                    item[key] = Object(**val)
        return item
    return recurse(item)

def object2data(item):
    def recurse(item):
        if isinstance( item, (list,tuple) ):
            _iter = enumerate(item)
        else:
            _iter = list(item.items())
        for key, val in _iter:
            if isinstance(val, ARMObject):
                item[key] = val.data()
            elif isinstance(val, (list, dict)):
                item[key] = recurse(val)
        return item
    return recurse(item)

def map_attrs( cls, item ):
    if isinstance( item, cls ):
        item = item.data()
    for key in item:
        if isinstance(item[key], ARMObject):
            map_attrs(item[key].__class__, item[key])
            continue
        if not cls.__spec__.get('attr_map')\
        or key not in cls.attr_map:
            continue
        key_map = cls.__spec__['attr_map'][key]
        if isinstance( new_key, str ):
            obj[key_map] = item.pop(key)
        else:
            nested_key = list(key_map.keys())[0]
            if nested_key not in obj:
                obj[nested_key] = {}
            obj[nested_key][key_map[nested_key]] = obj.pop(key)

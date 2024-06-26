from .arm.object import ARMObject, _object_cache
from .arm.attr import Attr


def get_object_cls(item):
    cls = None
    for Object in _object_cache:
        if Object.__spec__['object'] != item.get('object'):
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
        if isinstance(item, (list, tuple)):
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
                if item is base:
                    del base[key]
                recurse(val, new_key + '[{}]')
        return base

    return recurse(base)


def data2object(item, field_map=set(), session=None):
    def recurse(item):
        if isinstance(item, (list, tuple)):
            _iter = enumerate(item)
        else:
            convert_fieldmap(item, field_map)
            _iter = list(item.items())
        for key, val in _iter:
            if isinstance(val, (list, dict)):
                item[key] = recurse(val)
            if isinstance(val, dict) and val.get('object'):
                Object = get_object_cls(val)
                if Object:
                    if session:
                        val['_session'] = session
                    item[key] = Object(**val)
        return item

    return recurse(item)


def convert_fieldmap(obj, field_map):
    for f in field_map:
        if 'type' not in obj:
            continue
        if obj['type'] not in obj:
            obj[obj['type']] = {}
        if f in obj:
            obj[obj['type']][f] = obj.pop(f)


def object2data(item):
    def recurse(item):
        if isinstance(item, (list, tuple)):
            _iter = enumerate(item)
        else:
            if isinstance(item, ARMObject):
                item = item.data()
            _iter = list(item.items())
        for key, val in _iter:
            if isinstance(val, ARMObject):
                item[key] = val.data()
            elif isinstance(val, (list, dict)):
                item[key] = recurse(val)
        return item

    return recurse(item)

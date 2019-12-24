import os
import re
import sys

import payload
import requests
import copy

from ..utils import (convert_fieldmap, map_attrs, map_object,
                     nested_qstring_keys, object2data)
from .attr import Attr
from .object import ARMObject

if sys.version_info >= (3,0):
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

class ARMRequest(object):

    def __init__(self, Object=None):
        self.Object = Object
        self._filters  = []
        self._attrs    = []
        self._group_by = []

    def _request(self, method, id=None, headers=None, params=None, json=None):
        endpoint = self.Object.__spec__['endpoint']
        headers  = headers or {}
        params   = nested_qstring_keys(params or {})
        auth     = (payload.api_key, '')
        files    = {}

        flat_data = nested_qstring_keys(copy.deepcopy(json))
        for k in list(flat_data):
            if hasattr(flat_data[k], 'read'): files[k] = flat_data.pop(k)

        if id: endpoint = os.path.join(endpoint, id)

        if self._filters:
            for k, v in dict( (f.attr, f.opval) for f in self._filters ).items():
                if k not in params: params[k] = v

        if self._attrs:
            params['fields'] = list(map(str,self._attrs))

        if self._group_by:
            params['group_by'] = list(map(str,self._group_by))

        convert_fieldmap(params, self.Object.field_map)
        if json:
            convert_fieldmap(json, self.Object.field_map)
        params = nested_qstring_keys(params)

        if files:
            response = getattr(requests, method)(
                urljoin(payload.api_url, endpoint.strip('/')),
                params=params,
                auth=auth,
                data=flat_data,
                files=files
                )
        else:
            response = getattr(requests, method)(
                urljoin(payload.api_url, endpoint.strip('/')),
                headers=headers,
                params=params,
                auth=auth,
                json=json
                )
        try:
            data = response.json()

            if not isinstance(data, dict):
                raise payload.UnknownResponse()
        except ValueError:
            if response.status_code == 500:
                raise payload.InternalServerError()
            else:
                raise payload.UnknownResponse()

        if response.status_code == 200:
            if data.get('object') == 'list':
                return list(map( map_object, data['values'] ))
            else:
                return map_object(data)
        else:
            for Error in payload.PayloadError.__subclasses__():
                if Error.__name__ != data.get('error_type') \
                or Error.http_code != response.status_code:
                    continue
                raise Error(data.get('description'), data)
            if response.status_code == 500:
                raise payload.InternalServerError(data.get('description'), data)
            raise payload.BadRequest(data.get('description'), data)

    def get(self, id, **params):
        if not id:
            raise ValueError('id cannot be empty')
        return self._request('get', id=id, params=params)

    def select(self, *fields):
        self._attrs.extend(fields)
        return self

    def group_by(self, *fields):
        self._group_by.extend(fields)
        return self

    def create(self, obj=None, **values):
        obj = obj or values
        if isinstance( obj, list ):
            for o in obj:
                if not self.Object and not isinstance( o, ARMObject ):
                    raise TypeError('Bulk create requires ARMObject object types')
                if not self.Object:
                    self.Object = o.__class__
                elif isinstance( o, dict ):
                    o.update(self.Object.__spec__.get('polymorphic',{}))
                elif not isinstance( o, self.Object ):
                    raise TypeError('Bulk create requires all objects to be of the same type')
            obj = { 'object': 'list', 'values': obj }
        elif isinstance( obj, dict ):
            obj.update(self.Object.__spec__.get('polymorphic',{}))

        obj = object2data(obj)
        return self._request('post', json=obj)

    def delete(self, objects=None):
        if isinstance( objects, list ):
            if not objects:
                raise ValueError('List must not be empty')
            for o in objects:
                if not isinstance( o, ARMObject ):
                    raise TypeError('Bulk create requires ARMObject object types')
                if not self.Object:
                    self.Object = o.__class__
                elif not isinstance( o, self.Object ):
                    raise TypeError('Bulk create requires all objects to be of the same type')
            delete_query = '|'.join([ obj.id for obj in objects ])
            return self._request('delete', params={'id': delete_query, 'mode': 'query'})
        elif isinstance( objects, ARMObject ):
            self.Object = objects.__class__
            return cls._request('delete', id=objects.id)
        elif objects is None and self.Object and self._filters:
            return self._request('delete', params={'mode':'query'})
        else:
            raise TypeError('Bulk create requires ARMObject object types')

    def update(self, objects=None, **values):
        if objects:
            if not isinstance( objects, list ):
                raise ValueError('first parameter must be a list of updates')
            if not objects or not isinstance( objects[0], (list, tuple) ):
                raise ValueError('first parameter must be a list of updates')
            for o, upd in objects:
                if not isinstance( o, ARMObject ):
                    raise TypeError('Bulk update requires ARMObject object types')
                if not self.Object:
                    self.Object = o.__class__
                elif not isinstance( o, self.Object ):
                    raise TypeError('Bulk update requires all objects to be of the same type')
            updates = { 'object': 'list', 'values':
                list(map( lambda upd: dict( upd[1], id=upd[0].id ), objects )) }
            return self._request('put', json=updates)
        return self._request('put', params={'mode':'query'}, json=values)

    def filter_by(self, *filters, **kw_filters):
        self._filters.extend(filters)
        for key, val in nested_qstring_keys(kw_filters).items():
            self._filters.append( getattr( Attr, key ) == val )
        return self

    def all(self):
        return self._request('get')

    def first(self):
        resp = self._request('get', params=dict(limit=1))
        if resp: return resp[0]

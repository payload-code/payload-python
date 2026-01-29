import inspect
import json as json_serializer
from unittest.mock import MagicMock, Mock, call, patch
from urllib.parse import urljoin

import pytest

import payload
import payload.objects as objects_module
from payload.arm.attr import Attr
from payload.arm.object import ARMObject
from payload.arm.request import ARMRequest
from payload.arm.session import Session
from payload.objects import Account, Payment, PaymentItem, Transaction
from payload.utils import (
    convert_fieldmap,
    data2object,
    get_object_cls,
    nested_qstring_keys,
    object2data,
)

arm_object_classes = []

for name, obj in inspect.getmembers(objects_module):
    if inspect.isclass(obj) and issubclass(obj, objects_module.ARMObject):
        if obj is objects_module.ARMObject:
            continue
        data = {'Object': obj, 'object': obj.__spec__.get('object')}
        if obj.__spec__.get('polymorphic'):
            data['polymorphic'] = obj.__spec__.get('polymorphic')
        arm_object_classes.append(data)


def assert_mock_get_called_with_correct_values(
    arm_request,
    mock_req,
    expected_url=None,
    expected_params=None,
    expected_auth=None,
    expected_files=None,
):
    kwargs = dict(
        params=expected_params or {},
        auth=expected_auth or (arm_request.session.api_key, ''),
    )

    if expected_url is None:
        expected_url = urljoin(
            arm_request.session.api_url,
            arm_request.Object.__spec__['endpoint'].strip('/'),
        )

    if expected_files:
        kwargs.update(dict(files=expected_files, data={}, headers={}))
    else:
        kwargs.update(dict(json=None, headers={}))

    mock_req.assert_called_with(expected_url, **kwargs)


class MockArmObject(ARMObject):
    __spec__ = {'object': 'test'}


@pytest.fixture(scope='function')
def arm_request_from_class(arm_object_class, mock_session):
    return ARMRequest(Object=arm_object_class['Object'], session=mock_session)


@pytest.fixture
def mock_session():
    return Mock(api_url='test', api_key='test', api_version=None)


@pytest.fixture
def mock_response():
    return Mock()


@pytest.fixture
def arm_request(mock_session):
    return ARMRequest(Object=MockArmObject, session=mock_session)


def test_armrequest_init():
    session = Mock()
    arm_request = ARMRequest(MockArmObject, session)
    assert arm_request.Object == MockArmObject
    assert arm_request.session == session
    assert not arm_request._filters
    assert not arm_request._attrs
    assert not arm_request._group_by


@pytest.mark.parametrize(
    'test_case',
    [
        {
            'obj': MockArmObject(_session=Mock(), name='Test Object'),
            'expected_json': {'name': 'Test Object'},
        },
        {'obj': {'name': 'Test Object'}, 'expected_json': {'name': 'Test Object'}},
        {
            'obj': [MockArmObject(_session=Mock(), name='Test Object') for _ in range(2)],
            'expected_json': {
                'object': 'list',
                'values': [{'name': 'Test Object'}, {'name': 'Test Object'}],
            },
        },
        {
            'obj': [{'name': 'John'}, {'name': 'Doe'}],
            'expected_json': {
                'object': 'list',
                'values': [{'name': 'John'}, {'name': 'Doe'}],
            },
        },
        {
            'arm_request': ARMRequest(Object=None, session=Mock()),
            'obj': [Mock()],
            'expected_exception': TypeError,
            'expected_exception_message': 'Bulk create requires ARMObject object types',
        },
        {
            'obj': [Account(), Transaction()],
            'expected_exception': TypeError,
            'expected_exception_message': (
                'Bulk create requires all objects to be of the same type'
            ),
        },
        {'obj': [], 'expected_json': {}},
    ],
    ids=[
        'single_armobject',
        'single_dictionary',
        'multi_armobjects',
        'multi_dictionaries',
        'incorrect_object_type',
        'objects_of_different_types',
        'empty_list',
    ],
)
@patch('payload.arm.request.ARMRequest._request')
def test_armrequest_create(mock_request, test_case, arm_request):
    if 'arm_request' in test_case:
        arm_request = test_case['arm_request']

    if expected_exception := test_case.get('expected_exception'):
        with pytest.raises(expected_exception) as exc_info:
            arm_request.create(obj=test_case['obj'])
        assert str(exc_info.value) == test_case['expected_exception_message']
    else:
        arm_request.create(obj=test_case['obj'])
        mock_request.assert_called_once_with('post', json=test_case['expected_json'])


@pytest.mark.parametrize(
    'test_case',
    [
        {
            'objects': MockArmObject(_session=Mock(), name='Test Object', id='1'),
            'expected_call': call('delete', id='1'),
        },
        {
            'objects': [
                MockArmObject(_session=Mock(), name='Test Object', id=str(i + 1))
                for i in range(2)
            ],
            'expected_call': call('delete', params={'id': '1|2', 'mode': 'query'}),
        },
        {
            'objects': None,
            'filters': ['test_filter'],
            'expected_call': call('delete', params={'mode': 'query'}),
        },
        {
            'objects': 'invalid_object',
            'expected_exception': TypeError,
            'expected_exception_message': 'Bulk delete requires ARMObject object types',
        },
        {
            'objects': [],
            'expected_exception': ValueError,
            'expected_exception_message': 'List must not be empty',
        },
        {
            'objects': [Mock()],
            'expected_exception': TypeError,
            'expected_exception_message': 'Bulk delete requires ARMObject object types',
        },
        {
            'objects': [Account(id='1'), Transaction(id='1')],
            'expected_exception': TypeError,
            'expected_exception_message': (
                'Bulk delete requires all objects to be of the same type'
            ),
        },
    ],
    ids=[
        'single_armobject',
        'multi_armobjects',
        'query_mode',
        'incorrect_object_type',
        'empty_list',
        'invalid_object',
        'objects_of_different_types',
    ],
)
@patch('payload.arm.request.ARMRequest._request')
def test_armrequest_delete(mock_request, test_case, arm_request):
    if 'filters' in test_case:
        arm_request._filters = test_case['filters']

    if expected_exception := test_case.get('expected_exception'):
        with pytest.raises(expected_exception) as exc_info:
            arm_request.delete(objects=test_case['objects'])
        assert str(exc_info.value) == test_case['expected_exception_message']
    else:
        arm_request.delete(objects=test_case['objects'])
        expected_call = test_case['expected_call']
        actual_call = mock_request.call_args
        assert actual_call == expected_call


@pytest.mark.parametrize(
    'test_case',
    [
        {
            'objects': [
                (
                    MockArmObject(_session=Mock(), name='Test Object', id='1'),
                    {'name': 'Updated Object'},
                )
            ],
            'values': {},
            'expected_json': {
                'object': 'list',
                'values': [{'id': '1', 'name': 'Updated Object'}],
            },
        },
        {
            'objects': [({'id': '1', 'name': 'Test Object'}, {'name': 'Updated Object'})],
            'values': {},
            'expected_exception': TypeError,
            'expected_exception_message': 'Bulk update requires ARMObject object types',
        },
        {
            'objects': [
                (
                    MockArmObject(_session=Mock(), id='1', name='Test Object 1'),
                    {'name': 'Updated Object 1'},
                ),
                (
                    MockArmObject(_session=Mock(), id='2', name='Test Object 2'),
                    {'name': 'Updated Object 2'},
                ),
            ],
            'values': {},
            'expected_json': {
                'object': 'list',
                'values': [
                    {'name': 'Updated Object 1', 'id': '1'},
                    {'name': 'Updated Object 2', 'id': '2'},
                ],
            },
        },
        {
            'objects': [
                ({'id': '1', 'name': 'Test Object 1'}, {'name': 'Updated Object 1'}),
                ({'id': '2', 'name': 'Test Object 2'}, {'name': 'Updated Object 2'}),
            ],
            'values': {},
            'expected_exception': TypeError,
            'expected_exception_message': 'Bulk update requires ARMObject object types',
        },
        {
            'objects': [],
            'values': {},
            'expected_json': {},
            'expected_params': {'mode': 'query'},
        },
        {
            'objects': [],
            'values': {'name': 'Updated Object'},
            'expected_json': {'name': 'Updated Object'},
            'expected_params': {'mode': 'query'},
        },
        {
            'objects': 'invalid_object',
            'values': {'test_key': 'test_value'},
            'expected_exception': ValueError,
            'expected_exception_message': 'first parameter must be a list of updates',
        },
        {
            'objects': ['invalid_object'],
            'values': {'test_key': 'test_value'},
            'expected_exception': ValueError,
            'expected_exception_message': 'first parameter must be a list of updates',
        },
        {
            'objects': [
                (Transaction(), {'name': 'Updated Object 1'}),
                (Account(), {'name': 'Updated Object 2'}),
            ],
            'values': {},
            'expected_exception': TypeError,
            'expected_exception_message': (
                'Bulk update requires all objects to be of the same type'
            ),
        },
    ],
    ids=[
        'single_armobject',
        'mutli_values',
        'multi_armobjects',
        'multi_dict',
        'empty_list_no_values',
        'empty_list_with_values',
        'incorrect_object_type',
        'invalid_object_list',
        'objects_of_different_types',
    ],
)
@patch('payload.arm.request.ARMRequest._request')
def test_armrequest_update(mock_request, test_case, arm_request):
    if expected_exception := test_case.get('expected_exception'):
        with pytest.raises(expected_exception) as exc_info:
            arm_request.update(objects=test_case['objects'], **test_case['values'])
        assert str(exc_info.value) == test_case['expected_exception_message']
    else:
        arm_request.update(objects=test_case['objects'], **test_case['values'])
        if test_case.get('expected_params'):
            mock_request.assert_called_once_with(
                'put',
                params=test_case['expected_params'],
                json=test_case['expected_json'],
            )
        else:
            mock_request.assert_called_once_with('put', json=test_case['expected_json'])


@pytest.mark.parametrize(
    'attrs, expected_filters',
    [
        (
            dict(attr1='value1', attr2='value2'),
            [['attr1', 'value1', 'value1'], ['attr2', 'value2', 'value2']],
        ),
        (dict(attr=dict(nested='value')), [['attr[nested]', 'value', 'value']]),
        ([Attr.attr1 == 'value1'], [['attr1', 'value1', 'value1']]),
        ([Attr.attr1 != 'value1'], [['attr1', '!value1', 'value1']]),
        ([Attr.attr1 > 'value1'], [['attr1', '>value1', 'value1']]),
        ([Attr.attr1 >= 'value1'], [['attr1', '>=value1', 'value1']]),
        ([Attr.attr1 < 'value1'], [['attr1', '<value1', 'value1']]),
        ([Attr.attr1 <= 'value1'], [['attr1', '<=value1', 'value1']]),
        ([Attr.attr1.contains('value1')], [['attr1', '?*value1', 'value1']]),
        ([Attr.attr1.func() == 'value1'], [['func(attr1)', 'value1', 'value1']]),
        ([Attr.attr1.nested.func() == 'value1'], [['func(attr1[nested])', 'value1', 'value1']]),
        (
            [Attr.attr1.nested.func() != 'value1'],
            [['func(attr1[nested])', '!value1', 'value1']],
        ),
    ],
)
def test_armrequest_filter_by(arm_request, attrs, expected_filters):
    if isinstance(attrs, dict):
        request = arm_request.filter_by(**attrs)
    else:
        request = arm_request.filter_by(*attrs)

    assert len(arm_request._filters) == len(expected_filters)

    for i, (attr, opval, val) in enumerate(expected_filters):
        assert arm_request._filters[i].attr == attr
        assert arm_request._filters[i].opval == opval
        assert arm_request._filters[i].val == val


def test_armrequest_all(arm_request):
    with patch.object(ARMRequest, '_request') as mock_request:
        arm_request.all()
        mock_request.assert_called_with('get')


def test_armrequest_select(arm_request):
    with patch.object(ARMRequest, '_request'):
        arm_request.select('test_field')
        assert arm_request._attrs == ['test_field']


def test_armrequest_first(arm_request):
    with patch.object(ARMRequest, '_request') as mock_request:
        mock_request.return_value = [{'field1': 'value1'}, {'field2': 'value2'}]
        result = arm_request.first()

        mock_request.assert_called_with('get', params={'limit': 1})

        assert result == mock_request.return_value[0]


def test_armrequest_group_by(arm_request):
    arm_request.group_by('test_field')
    assert arm_request._group_by == ['test_field']


def test_armrequest_order_by(arm_request):
    result = arm_request.order_by('test_field')
    assert arm_request._order_by == ['test_field']
    assert result is arm_request


def test_armrequest_order_by_multiple_fields(arm_request):
    arm_request.order_by('field1', 'field2')
    assert arm_request._order_by == ['field1', 'field2']


def test_armrequest_order_by_chaining(arm_request):
    arm_request.order_by('field1').order_by('field2')
    assert arm_request._order_by == ['field1', 'field2']


def test_armrequest_limit(arm_request):
    result = arm_request.limit(10)
    assert arm_request._limit == 10
    assert result is arm_request


def test_armrequest_limit_overwrite(arm_request):
    arm_request.limit(10).limit(20)
    assert arm_request._limit == 20


def test_armrequest_offset(arm_request):
    result = arm_request.offset(5)
    assert arm_request._offset == 5
    assert result is arm_request


def test_armrequest_offset_overwrite(arm_request):
    arm_request.offset(5).offset(10)
    assert arm_request._offset == 10


def test_armrequest_limit_offset_chaining(arm_request):
    result = arm_request.limit(10).offset(5)
    assert arm_request._limit == 10
    assert arm_request._offset == 5
    assert result is arm_request


def test_armrequest_getitem_with_slice(arm_request):
    mock_results = [{'id': str(i)} for i in range(10, 20)]

    with patch.object(ARMRequest, '_request', return_value=mock_results):
        result = arm_request[10:20]

        # Verify offset and limit were set correctly
        assert arm_request._offset == 10
        assert arm_request._limit == 10

        # Verify .all() was called and returned results
        assert result == mock_results


def test_armrequest_getitem_with_slice_zero_start(arm_request):
    mock_results = [{'id': str(i)} for i in range(0, 10)]

    with patch.object(ARMRequest, '_request', return_value=mock_results):
        result = arm_request[0:10]

        # Zero start is falsy, so offset should not be set
        assert arm_request._offset is None
        assert arm_request._limit == 10

        # Verify .all() was called and returned results
        assert result == mock_results


def test_armrequest_getitem_with_slice_large_range(arm_request):
    mock_results = [{'id': str(i)} for i in range(100, 200)]

    with patch.object(ARMRequest, '_request', return_value=mock_results):
        result = arm_request[100:200]

        # Verify offset and limit were set correctly
        assert arm_request._offset == 100
        assert arm_request._limit == 100

        # Verify .all() was called and returned results
        assert result == mock_results


def test_armrequest_getitem_with_slice_none_start(arm_request):
    """Test slice with None start [:20]"""
    mock_results = [{'id': str(i)} for i in range(0, 20)]

    with patch.object(ARMRequest, '_request', return_value=mock_results):
        result = arm_request[:20]

        # None start means no offset
        assert arm_request._offset is None
        assert arm_request._limit == 20

        # Verify results returned
        assert result == mock_results


def test_armrequest_getitem_with_slice_none_stop(arm_request):
    """Test slice with None stop [10:]"""
    mock_results = [{'id': str(i)} for i in range(10, 100)]

    with patch.object(ARMRequest, '_request', return_value=mock_results):
        result = arm_request[10:]

        # Should set offset but not limit
        assert arm_request._offset == 10
        assert arm_request._limit is None

        # Verify results returned
        assert result == mock_results


def test_armrequest_getitem_with_slice_both_none(arm_request):
    """Test slice with both None [:]"""
    mock_results = [{'id': str(i)} for i in range(0, 100)]

    with patch.object(ARMRequest, '_request', return_value=mock_results):
        result = arm_request[:]

        # Neither offset nor limit should be set
        assert arm_request._offset is None
        assert arm_request._limit is None

        # Verify results returned (equivalent to .all())
        assert result == mock_results


def test_armrequest_getitem_with_integer_raises_typeerror(arm_request):
    with pytest.raises(TypeError) as exc_info:
        arm_request[5]
    assert 'invalid key or index: 5' in str(exc_info.value)


def test_armrequest_getitem_with_string_raises_typeerror(arm_request):
    with pytest.raises(TypeError) as exc_info:
        arm_request['invalid']
    assert 'invalid key or index: invalid' in str(exc_info.value)


def test_armrequest_getitem_with_none_raises_typeerror(arm_request):
    with pytest.raises(TypeError) as exc_info:
        arm_request[None]
    assert 'invalid key or index: None' in str(exc_info.value)


def test_armrequest_iter(arm_request):
    mock_results = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Item 2'},
        {'id': '3', 'name': 'Item 3'},
    ]

    with patch.object(ARMRequest, 'all', return_value=mock_results):
        results = list(arm_request)

        assert len(results) == 3
        assert results[0] == mock_results[0]
        assert results[1] == mock_results[1]
        assert results[2] == mock_results[2]


def test_armrequest_iter_empty(arm_request):
    with patch.object(ARMRequest, 'all', return_value=[]):
        results = list(arm_request)
        assert results == []


def test_armrequest_iter_in_for_loop(arm_request):
    mock_results = [{'id': '1', 'name': 'Item 1'}, {'id': '2', 'name': 'Item 2'}]

    with patch.object(ARMRequest, 'all', return_value=mock_results):
        collected = []
        for item in arm_request:
            collected.append(item)

        assert collected == mock_results


def test_armrequest_iter_with_comprehension(arm_request):
    mock_results = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Item 2'},
        {'id': '3', 'name': 'Item 3'},
    ]

    with patch.object(ARMRequest, 'all', return_value=mock_results):
        ids = [item['id'] for item in arm_request]
        assert ids == ['1', '2', '3']


def test_armrequest_iter_with_any(arm_request):
    mock_results = [{'id': '1', 'name': 'Item 1'}]

    with patch.object(ARMRequest, 'all', return_value=mock_results):
        assert any(arm_request) is True


def test_armrequest_iter_with_any_empty(arm_request):
    with patch.object(ARMRequest, 'all', return_value=[]):
        assert any(arm_request) is False


def test_armrequest_getitem_chaining_with_filter(arm_request):
    mock_results = [{'id': str(i), 'status': 'active'} for i in range(10, 20)]

    with patch.object(ARMRequest, '_request', return_value=mock_results):
        result = arm_request.filter_by(status='active')[10:20]

        # Verify filter was applied
        assert len(arm_request._filters) == 1

        # Verify offset and limit were set correctly
        assert arm_request._offset == 10
        assert arm_request._limit == 10

        # Verify .all() was called and returned results
        assert result == mock_results


def test_armrequest_request_files(arm_request, mock_response):
    test_files = {'file': Mock()}

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.post', return_value=mock_response) as mock_post:
        arm_request._request('post', json=test_files)

    assert_mock_get_called_with_correct_values(
        arm_request, mock_post, expected_files={'file': test_files['file']}
    )


def test_armrequest_request_id(arm_request, mock_response):
    test_id = '1'

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._request('get', id=test_id)

    assert_mock_get_called_with_correct_values(arm_request, mock_get, 'tests/1')


def test_armrequest_request_filters(arm_request, mock_response):
    test_filters = [
        Attr.filter_attr1 == 'filter_val1',
        Attr.filter_attr2 == 'filter_val2',
    ]

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._filters = test_filters
        arm_request._request('get')

    assert_mock_get_called_with_correct_values(
        arm_request,
        mock_get,
        expected_params={'filter_attr1': 'filter_val1', 'filter_attr2': 'filter_val2'},
    )


def test_armrequest_request_group_by(arm_request, mock_response):
    test_group_by = ['group1', 'group2']

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._group_by = test_group_by
        arm_request._request('get')

    expected_params = {'group_by[0]': 'group1', 'group_by[1]': 'group2'}

    assert_mock_get_called_with_correct_values(
        arm_request, mock_get, expected_params=expected_params
    )


def test_armrequest_request_order_by(arm_request, mock_response):
    test_order_by = ['field1', 'field2']

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._order_by = test_order_by
        arm_request._request('get')

    expected_params = {'order_by[0]': 'field1', 'order_by[1]': 'field2'}

    assert_mock_get_called_with_correct_values(
        arm_request, mock_get, expected_params=expected_params
    )


def test_armrequest_request_order_by_single_field(arm_request, mock_response):
    test_order_by = ['created_at']

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._order_by = test_order_by
        arm_request._request('get')

    expected_params = {'order_by[0]': 'created_at'}

    assert_mock_get_called_with_correct_values(
        arm_request, mock_get, expected_params=expected_params
    )


def test_armrequest_request_limit(arm_request, mock_response):
    test_limit = 10

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._limit = test_limit
        arm_request._request('get')

    expected_params = {'limit': '10'}

    assert_mock_get_called_with_correct_values(
        arm_request, mock_get, expected_params=expected_params
    )


def test_armrequest_request_offset(arm_request, mock_response):
    test_offset = 5

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._offset = test_offset
        arm_request._request('get')

    expected_params = {'offset': '5'}

    assert_mock_get_called_with_correct_values(
        arm_request, mock_get, expected_params=expected_params
    )


def test_armrequest_request_limit_and_offset(arm_request, mock_response):
    test_limit = 10
    test_offset = 20

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._limit = test_limit
        arm_request._offset = test_offset
        arm_request._request('get')

    expected_params = {'limit': '10', 'offset': '20'}

    assert_mock_get_called_with_correct_values(
        arm_request, mock_get, expected_params=expected_params
    )


def test_armrequest_request_order_by_limit_offset(arm_request, mock_response):
    test_order_by = ['created_at']
    test_limit = 10
    test_offset = 5

    response_data = {'object': arm_request.Object.__spec__['object']}
    mock_response.text = json_serializer.dumps(response_data)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request._order_by = test_order_by
        arm_request._limit = test_limit
        arm_request._offset = test_offset
        arm_request._request('get')

    expected_params = {'order_by[0]': 'created_at', 'limit': '10', 'offset': '5'}

    assert_mock_get_called_with_correct_values(
        arm_request, mock_get, expected_params=expected_params
    )


def test_armrequest_request_params(arm_request, mock_response):
    test_params = {'param1': 'value1'}

    with patch('requests.get') as mock_get:
        response_data = {'object': arm_request.Object.__spec__['object']}
        mock_response.text = json_serializer.dumps(response_data)
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        arm_request._request('get', params=test_params)

        assert_mock_get_called_with_correct_values(
            arm_request, mock_get, expected_params=test_params
        )


def test_armrequest_request_500_resp_json_not_dict(arm_request):
    mock_response = Mock(status_code=500, text='[]')

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.UnknownResponse):
            arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_500_no_resp_json_500(arm_request):
    mock_response = Mock(status_code=500)
    mock_response.text = json_serializer.dumps({'details': 'test'})

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.InternalServerError):
            arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_unknown_response(arm_request):
    mock_response = Mock(status_code=999, text='null')

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.UnknownResponse):
            arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_200_list(arm_request, mock_response):
    test_list_response = {
        'object': 'list',
        'values': [{'id': 1, 'name': 'Test 1'}, {'id': 2, 'name': 'Test 2'}],
    }

    mock_response.text = json_serializer.dumps(test_list_response)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        result = arm_request._request('get')

        assert len(result) == len(test_list_response['values'])
        assert result[0]['name'] == test_list_response['values'][0]['name']
        assert result[1]['name'] == test_list_response['values'][1]['name']

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_200_single_obj(arm_request, mock_response):
    test_object_response = {'object': 'single', 'id': 1, 'name': 'Test 1'}

    mock_response.text = json_serializer.dumps(test_object_response)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        result = arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)
        assert isinstance(result, dict)
        assert result['name'] == 'Test 1'


def test_armrequest_request_uses_dotdict_object_hook():
    """Test that DotDict class provides dot notation access to dict keys"""
    from payload.arm.request import DotDict

    # Test DotDict functionality directly
    test_dict = DotDict({'key1': 'value1', 'key2': 'value2', 'nested': {'inner': 'value'}})

    # Test dot notation access
    assert test_dict.key1 == 'value1'
    assert test_dict.key2 == 'value2'

    # Test that dict access still works
    assert test_dict['key1'] == 'value1'
    assert test_dict['key2'] == 'value2'

    # Test nested dict (note: nested dicts need to be DotDict too for dot access)
    nested_dotdict = DotDict(
        {'outer': DotDict({'inner': DotDict({'deep': 'value'})})}
    )
    assert nested_dotdict.outer.inner.deep == 'value'
    assert nested_dotdict['outer']['inner']['deep'] == 'value'

    # Test setting attributes
    test_dict.new_key = 'new_value'
    assert test_dict.new_key == 'new_value'
    assert test_dict['new_key'] == 'new_value'

    # Test deleting attributes
    del test_dict.new_key
    assert 'new_key' not in test_dict


def test_armrequest_request_dotdict_with_json_parsing():
    """Test that DotDict works correctly when used as object_hook in JSON parsing"""
    from payload.arm.request import DotDict

    # Test basic dot notation access after JSON parsing
    data = json_serializer.loads(
        '{"key1": "value1", "key2": "value2"}', object_hook=DotDict
    )
    assert data.key1 == 'value1'
    assert data.key2 == 'value2'

    # Test nested objects - object_hook ensures all dicts become DotDict
    nested_data = json_serializer.loads(
        '{"outer": {"inner": {"deep": "value"}}}', object_hook=DotDict
    )
    assert nested_data.outer.inner.deep == 'value'

    # Test that dict access still works
    assert nested_data['outer']['inner']['deep'] == 'value'

    # Test mixed access
    assert nested_data.outer['inner'].deep == 'value'

    # Test with lists containing objects (avoid 'items' key due to dict.items() method)
    list_data = json_serializer.loads(
        '{"records": [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]}',
        object_hook=DotDict,
    )
    assert list_data.records[0].id == 1
    assert list_data.records[0].name == 'first'
    assert list_data.records[1].id == 2
    assert list_data.records[1].name == 'second'

    # Test that traditional dict methods still work
    assert 'records' in list_data
    assert len(list_data) == 1
    assert list(list_data.keys()) == ['records']


def test_armrequest_request_dotdict_with_list_response(arm_request, mock_response):
    """Test that DotDict works correctly with list responses"""
    test_list_response = {
        'object': 'list',
        'values': [
            {'id': 1, 'name': 'Item 1', 'status': 'active'},
            {'id': 2, 'name': 'Item 2', 'status': 'pending'},
        ],
    }

    mock_response.text = json_serializer.dumps(test_list_response)
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        result = arm_request._request('get')

        # Verify list response structure
        assert len(result) == 2

        # Test that items in the list support dot notation
        assert result[0].id == 1
        assert result[0].name == 'Item 1'
        assert result[0].status == 'active'

        assert result[1].id == 2
        assert result[1].name == 'Item 2'
        assert result[1].status == 'pending'

        # Traditional dict access should still work
        assert result[0]['name'] == 'Item 1'
        assert result[1]['name'] == 'Item 2'


def test_armrequest_request_raise_non_500_errors(arm_request):
    with patch(
        'requests.get',
        return_value=Mock(
            status_code=400, text=json_serializer.dumps({'error_type': 'BadRequest'})
        ),
    ) as mock_get:
        with pytest.raises(payload.BadRequest):
            arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_raise_bad_request(arm_request, mock_response):
    mock_response.text = json_serializer.dumps({})
    mock_response.status_code = 400

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.BadRequest):
            arm_request._request('get')

    assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_non_matching_error_and_http_code(arm_request):
    with patch(
        'requests.get',
        return_value=Mock(
            status_code=400,
            text=json_serializer.dumps({'error_type': 'InternalServerError'}),
        ),
    ) as mock_get:
        with pytest.raises(payload.BadRequest):
            arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_error_name_neq_data_error_type(arm_request):
    with patch(
        'requests.get',
        return_value=Mock(
            status_code=500, text=json_serializer.dumps({'error_type': 'BadRequest'})
        ),
    ) as mock_get:
        with pytest.raises(payload.InternalServerError):
            arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


def test_armrequest_request_500_raise_internal_server_error(arm_request, mock_response):
    mock_response.text = json_serializer.dumps({})
    mock_response.status_code = 500

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.InternalServerError):
            arm_request._request('get')

        assert_mock_get_called_with_correct_values(arm_request, mock_get)


# Test get_object_cls
@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_get_object_cls(arm_object_class):
    item_data = {'object': arm_object_class['object']}
    if 'polymorphic' in arm_object_class:
        item_data.update(arm_object_class['polymorphic'])
    expected = arm_object_class['Object']
    assert get_object_cls(item_data) == expected


# Test convert_fieldmap
@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_convert_fieldmap_on_arm_object_classes(arm_object_class):
    obj = {'type': arm_object_class['object']}
    field_map = set(arm_object_class.keys()) - {'Object', 'object', 'polymorphic'}
    expected = obj.copy()
    if mapped_fields := {k: arm_object_class[k] for k in field_map}:
        expected[arm_object_class['object']] = mapped_fields
    convert_fieldmap(obj, field_map)
    assert obj == expected


@pytest.mark.parametrize(
    'item, expected',
    [
        (
            {
                'object': 'transaction',
                'payment': Payment(amount=100),
                'data': {'list': [1, 2, 3]},
            },
            {
                'object': 'transaction',
                'payment': {'type': 'payment', 'amount': 100},
                'data': {'list': [1, 2, 3]},
            },
        ),
        (
            {'object': 'transaction', 'payment': Payment(), 'data': {}},
            {'object': 'transaction', 'payment': {'type': 'payment'}, 'data': {}},
        ),
        (
            {
                'object': 'transaction',
                'payments': [Payment(amount=100), Payment(amount=200)],
            },
            {
                'object': 'transaction',
                'payments': [
                    {'type': 'payment', 'amount': 100},
                    {'type': 'payment', 'amount': 200},
                ],
            },
        ),
        (
            {'object': 'transaction', 'payment': {'type': 'payment'}},
            {'object': 'transaction', 'payment': {'type': 'payment'}},
        ),
        (
            {
                'object': 'transaction',
                'payment': PaymentItem(amount=100),
                'data': {'list': [1, 2, 3]},
            },
            {
                'object': 'transaction',
                'payment': {'entry_type': 'payment', 'amount': 100},
                'data': {'list': [1, 2, 3]},
            },
        ),
    ],
)
def test_object2data(item, expected):
    assert object2data(item) == expected


@pytest.mark.parametrize(
    'obj, field_map, expected',
    [
        # Test case 1: Object without 'type' attribute
        ({}, {'field1', 'field2'}, {}),
        # Test case 2: Object with 'type' but field not present
        ({'type': 'payment'}, {'field1', 'field2'}, {'type': 'payment', 'payment': {}}),
        # Test case 3: Object with 'type' and field present
        (
            {'type': 'payment', 'payment': {}, 'field1': 'value1', 'field2': 'value2'},
            {'field1', 'field2'},
            {'type': 'payment', 'payment': {'field1': 'value1', 'field2': 'value2'}},
        ),
        # Test case 4: Object with 'type' and field already nested under type
        (
            {'type': 'payment', 'payment': {'field1': 'value1'}},
            {'field1'},
            {'type': 'payment', 'payment': {'field1': 'value1'}},
        ),
        # Test case 5: Object with 'type' and field already nested under type (field map not in object)
        (
            {'type': 'payment', 'payment': {'field1': 'value1'}},
            {'field2'},
            {'type': 'payment', 'payment': {'field1': 'value1'}},
        ),
    ],
)
def test_convert_fieldmap(obj, field_map, expected):
    convert_fieldmap(obj, field_map)
    assert obj == expected


@pytest.mark.parametrize(
    'base, expected',
    [
        # Test case 1: Empty base
        ({}, {}),
        # Test case 2: Single-level dictionary
        ({'key1': 'value1', 'key2': 'value2'}, {'key1': 'value1', 'key2': 'value2'}),
        # Test case 3: Nested dictionary
        (
            {'key1': 'value1', 'key2': {'nested1': 'value3', 'nested2': 'value4'}},
            {'key1': 'value1', 'key2[nested1]': 'value3', 'key2[nested2]': 'value4'},
        ),
        # Test case 4: Nested dictionary with empty values
        (
            {'key1': 'value1', 'key2': {'nested1': '', 'nested2': 'value4'}},
            {'key1': 'value1', 'key2[nested1]': '', 'key2[nested2]': 'value4'},
        ),
        # Test case 5: Nested dictionary with list
        (
            {
                'key1': 'value1',
                'key2': {'nested1': ['item1', 'item2'], 'nested2': 'value4'},
            },
            {
                'key1': 'value1',
                'key2[nested1][0]': 'item1',
                'key2[nested1][1]': 'item2',
                'key2[nested2]': 'value4',
            },
        ),
        # Test case 6: Nested dictionary with tuple
        (
            {
                'key1': 'value1',
                'key2': {'nested1': ('item1', 'item2'), 'nested2': 'value4'},
            },
            {
                'key1': 'value1',
                'key2[nested1][0]': 'item1',
                'key2[nested1][1]': 'item2',
                'key2[nested2]': 'value4',
            },
        ),
    ],
)
def test_nested_qstring_keys(base, expected):
    assert nested_qstring_keys(base) == expected, 'Failed for base: {}'.format(base)


@pytest.mark.parametrize(
    'item, field_map, session, expected',
    [
        (
            {'field1': 'value1', 'field2': 'value2'},
            {'field1', 'field2'},
            None,
            {'field1': 'value1', 'field2': 'value2'},
        ),
        (
            {'type': 'payment', 'payment': {'field1': 'value1', 'field2': 'value2'}},
            {'field1', 'field2'},
            None,
            {'type': 'payment', 'payment': {'field1': 'value1', 'field2': 'value2'}},
        ),
    ],
)
def test_data2object(item, field_map, session, expected):
    result = data2object(item, field_map, session)
    assert result == expected


class MockObject(ARMObject):
    __spec__ = {'object': 'mock_object', 'endpoint': '/mock'}


class TestARMRequestApiVersion:
    """Unit tests for ARMRequest._request api_version header functionality"""

    @patch('payload.arm.request.requests')
    def test_api_version_header_included_when_set(self, mock_requests):
        """Test that X-API-Version header is included when session.api_version is set"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {
            'object': 'mock_object',
            'id': 'mock_123',
        }
        mock_response.text = json_serializer.dumps(response_data)
        mock_requests.get.return_value = mock_response

        # Create session with api_version
        session = Session(
            api_key='test_key', api_url='https://api.test.com', api_version='v2.1'
        )

        # Create request and execute
        request = ARMRequest(Object=MockObject, session=session)
        request.get('mock_123')

        # Verify requests.get was called with X-API-Version header
        mock_requests.get.assert_called_once()
        call_kwargs = mock_requests.get.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-API-Version' in call_kwargs['headers']
        assert call_kwargs['headers']['X-API-Version'] == 'v2.1'

    @patch('payload.arm.request.requests')
    def test_api_version_header_not_included_when_none(self, mock_requests):
        """Test that X-API-Version header is not included when session.api_version is None"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {
            'object': 'mock_object',
            'id': 'mock_123',
        }
        mock_response.text = json_serializer.dumps(response_data)
        mock_requests.get.return_value = mock_response

        # Create session without api_version
        session = Session(api_key='test_key', api_url='https://api.test.com', api_version=None)

        # Create request and execute
        request = ARMRequest(Object=MockObject, session=session)
        request.get('mock_123')

        # Verify requests.get was called without X-API-Version header
        mock_requests.get.assert_called_once()
        call_kwargs = mock_requests.get.call_args[1]
        headers = call_kwargs.get('headers', {})
        assert 'X-API-Version' not in headers

    @patch('payload.arm.request.requests')
    @patch('payload.api_version', 'v2.2')
    def test_api_version_header_uses_global_payload_when_no_session(self, mock_requests):
        """Test that X-API-Version header uses global payload.api_version when no session provided"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {
            'object': 'mock_object',
            'id': 'mock_123',
        }
        mock_response.text = json_serializer.dumps(response_data)
        mock_requests.get.return_value = mock_response

        # Create request without session (will use global payload module)
        request = ARMRequest(Object=MockObject, session=None)
        request.get('mock_123')

        # Verify requests.get was called with X-API-Version header from global payload
        mock_requests.get.assert_called_once()
        call_kwargs = mock_requests.get.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-API-Version' in call_kwargs['headers']
        assert call_kwargs['headers']['X-API-Version'] == 'v2.2'

    @patch('payload.arm.request.requests')
    def test_api_version_header_in_post_request(self, mock_requests):
        """Test that X-API-Version header is included in POST requests"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {
            'object': 'mock_object',
            'id': 'mock_123',
        }
        mock_response.text = json_serializer.dumps(response_data)
        mock_requests.post.return_value = mock_response

        # Create session with api_version
        session = Session(
            api_key='test_key', api_url='https://api.test.com', api_version='v2.3'
        )

        # Create request and execute
        request = ARMRequest(Object=MockObject, session=session)
        request.create({'field': 'value'})

        # Verify requests.post was called with X-API-Version header
        mock_requests.post.assert_called_once()
        call_kwargs = mock_requests.post.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-API-Version' in call_kwargs['headers']
        assert call_kwargs['headers']['X-API-Version'] == 'v2.3'

    @patch('payload.arm.request.requests')
    def test_api_version_header_in_put_request(self, mock_requests):
        """Test that X-API-Version header is included in PUT requests"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {
            'object': 'mock_object',
            'id': 'mock_123',
        }
        mock_response.text = json_serializer.dumps(response_data)
        mock_requests.put.return_value = mock_response

        # Create session with api_version
        session = Session(
            api_key='test_key', api_url='https://api.test.com', api_version='v2.4'
        )

        # Create request and execute update
        request = ARMRequest(Object=MockObject, session=session)
        request.update(field='new_value')

        # Verify requests.put was called with X-API-Version header
        mock_requests.put.assert_called_once()
        call_kwargs = mock_requests.put.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-API-Version' in call_kwargs['headers']
        assert call_kwargs['headers']['X-API-Version'] == 'v2.4'

    @patch('payload.arm.request.requests')
    def test_api_version_header_in_delete_request(self, mock_requests):
        """Test that X-API-Version header is included in DELETE requests"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {
            'object': 'mock_object',
            'id': 'mock_123',
        }
        mock_response.text = json_serializer.dumps(response_data)
        mock_requests.delete.return_value = mock_response

        # Create session with api_version
        session = Session(
            api_key='test_key', api_url='https://api.test.com', api_version='v2.5'
        )

        # Create mock object to delete
        mock_obj = MockObject()
        mock_obj.id = 'mock_123'

        # Create request and execute delete
        request = ARMRequest(Object=MockObject, session=session)
        request.delete(mock_obj)

        # Verify requests.delete was called with X-API-Version header
        mock_requests.delete.assert_called_once()
        call_kwargs = mock_requests.delete.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-API-Version' in call_kwargs['headers']
        assert call_kwargs['headers']['X-API-Version'] == 'v2.5'

    @patch('payload.arm.request.requests')
    def test_api_version_header_with_existing_headers(self, mock_requests):
        """Test that X-API-Version header is merged with existing headers"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {
            'object': 'mock_object',
            'id': 'mock_123',
        }
        mock_response.text = json_serializer.dumps(response_data)
        mock_requests.get.return_value = mock_response

        # Create session with api_version
        session = Session(
            api_key='test_key', api_url='https://api.test.com', api_version='v2.6'
        )

        # Create request and execute with custom headers
        request = ARMRequest(Object=MockObject, session=session)
        request._request('get', id='mock_123', headers={'X-Custom-Header': 'custom_value'})

        # Verify both headers are present
        mock_requests.get.assert_called_once()
        call_kwargs = mock_requests.get.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-API-Version' in call_kwargs['headers']
        assert 'X-Custom-Header' in call_kwargs['headers']
        assert call_kwargs['headers']['X-API-Version'] == 'v2.6'
        assert call_kwargs['headers']['X-Custom-Header'] == 'custom_value'

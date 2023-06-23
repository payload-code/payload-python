from payload.utils import (
    get_object_cls, map_object, nested_qstring_keys, data2object,
    convert_fieldmap, object2data, map_attrs
)

from payload.utils import get_object_cls
from mock import Mock, patch, call, create_autospec
import pytest
import payload
from unittest.mock import Mock, patch
from payload.arm.request import ARMRequest
from urllib.parse import urljoin

import inspect
import payload.objects as objects_module
from payload.objects import *
from payload.arm.attr import Attr


class MockObject:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


arm_object_classes = []

for name, obj in inspect.getmembers(objects_module):
    if inspect.isclass(obj) and issubclass(obj, objects_module.ARMObject):
        if obj == objects_module.ARMObject:
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
        expected_files=None
):
    if expected_url is None:
        expected_url = urljoin(arm_request.session.api_url, arm_request.Object.__spec__['endpoint'].strip('/'))

    if expected_auth is None:
        expected_auth = (arm_request.session.api_key, '')

    if expected_params is None:
        expected_params = {}

    if expected_files is None:
        expected_files = {}

    # if

    #
    # mock_req.assert_called_with(
    #     expected_url,
    #     headers={},
    #     params=expected_params,
    #     auth=expected_auth,
    #     json=None
    # )


class MockArmObject(ARMObject):
    __spec__ = {'object': 'test'}


@pytest.fixture(scope='function')
def arm_request_from_class(arm_object_class, mock_session):
    return ARMRequest(Object=arm_object_class['Object'], session=mock_session)


@pytest.fixture
def mock_session():
    return Mock(api_url="test", api_key="test")


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
    assert arm_request._filters == []
    assert arm_request._attrs == []
    assert arm_request._group_by == []


@pytest.mark.parametrize("test_case", [
    {
        "description": "Creating with a single ARMObject",
        "obj": MockArmObject(_session=Mock(), name='Test Object'),
        "expected_json": {'name': 'Test Object'}
    },
    {
        "description": "Creating with a single dictionary",
        "obj": {'name': 'Test Object'},
        "expected_json": {'name': 'Test Object'}
    },
    {
        "description": "Creating with a list of ARMObjects (bulk)",
        "obj": [MockArmObject(_session=Mock(), name='Test Object') for _ in range(2)],
        "expected_json": {'object': 'list', 'values': [{'name': 'Test Object'}, {'name': 'Test Object'}]}
    },
    {
        "description": "Creating with a list of dictionaries (bulk)",
        "obj": [{"name": "John"}, {"name": "Doe"}],
        "expected_json": {'object': 'list', 'values': [{"name": "John"}, {"name": "Doe"}]}
    },
    {
        "description": "Creating with incorrect object type",
        "arm_request": ARMRequest(Object=None, session=Mock()),
        "obj": [Mock()],
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk create requires ARMObject object types'
    },
    {
        "description": "Creating with objects of different types in the list",
        "obj": [
            Account(),
            Transaction()
        ],
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk create requires all objects to be of the same type'
    },
    {
        "description": "Creating with empty object list",
        "obj": [],
        "expected_json": {}

    }
])
@patch('payload.arm.request.ARMRequest._request')
def test_armrequest_create(mock_request, test_case, arm_request):
    print(test_case["description"])
    if "arm_request" in test_case:
        arm_request = test_case["arm_request"]

    if "expected_exception" in test_case:
        with pytest.raises(test_case["expected_exception"]) as exc_info:
            arm_request.create(obj=test_case["obj"])
        assert str(exc_info.value) == test_case["expected_exception_message"]
    else:
        arm_request.create(obj=test_case["obj"])
        mock_request.assert_called_once_with('post', json=test_case["expected_json"])


@pytest.mark.parametrize("test_case", [
    {
        "description": "Deleting a single ARMObject",
        "objects": MockArmObject(_session=Mock(), name='Test Object', id='1'),
        "expected_call": call('delete', id='1')
    },
    {
        "description": "Deleting a list of ARMObjects (bulk)",
        "objects": [MockArmObject(_session=Mock(), name='Test Object', id=str(i + 1)) for i in range(2)],
        "expected_call": call('delete', params={'id': '1|2', 'mode': 'query'})
    },
    {
        "description": "Deleting with filters",
        "objects": None,
        "filters": ['test_filter'],
        "expected_call": call('delete', params={'mode': 'query'})
    },
    {
        "description": "Deleting with incorrect object type",
        "objects": "invalid_object",
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk delete requires ARMObject object types'
    },
    {
        "description": "Deleting with empty object list",
        "objects": [],
        "expected_exception": ValueError,
        "expected_exception_message": 'List must not be empty'
    },
    {
        "description": "Deleting with invalid object in the list",
        "objects": [Mock()],
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk delete requires ARMObject object types'
    },
    {
        "description": "Deleting with objects of different types in the list",
        "objects": [
            Account(id='1'),
            Transaction(id='1')
        ],
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk delete requires all objects to be of the same type'
    },
])
@patch('payload.arm.request.ARMRequest._request')
def test_armrequest_delete(mock_request, test_case, arm_request):
    print(test_case["description"])

    if 'filters' in test_case:
        arm_request._filters = test_case["filters"]

    if "expected_exception" in test_case:
        with pytest.raises(test_case["expected_exception"]) as exc_info:
            arm_request.delete(objects=test_case["objects"])
        assert str(exc_info.value) == test_case["expected_exception_message"]
    else:
        arm_request.delete(objects=test_case["objects"])
        if test_case.get("expected_call"):
            expected_call = test_case["expected_call"]
            actual_call = mock_request.call_args
            assert actual_call == expected_call


@pytest.mark.parametrize("test_case", [
    {
        "description": "Updating a single ARMObject",
        "objects": [(MockArmObject(_session=Mock(), name='Test Object', id='1'), {'name': 'Updated Object'})],
        "values": {},
        "expected_json": {'object': 'list', 'values': [{'id': '1', 'name': 'Updated Object'}]}
    },
    {
        "description": "Updating a dictionary with updated values",
        "objects": [({'id': '1', 'name': 'Test Object'}, {'name': 'Updated Object'})],
        "values": {},
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk update requires ARMObject object types'
    },
    {
        "description": "Updating with a list of ARMObjects (bulk)",
        "objects": [
            (MockArmObject(_session=Mock(), id='1', name='Test Object 1'), {'name': 'Updated Object 1'}),
            (MockArmObject(_session=Mock(), id='2', name='Test Object 2'), {'name': 'Updated Object 2'})
        ],
        "values": {},
        "expected_json": {
            'object': 'list',
            'values': [
                {'name': 'Updated Object 1', 'id': '1'},
                {'name': 'Updated Object 2', 'id': '2'}
            ]
        }
    },
    {
        "description": "Updating dictionaries with a list of dictionaries (bulk)",
        "objects": [
            ({'id': '1', 'name': 'Test Object 1'}, {'name': 'Updated Object 1'}),
            ({'id': '2', 'name': 'Test Object 2'}, {'name': 'Updated Object 2'})
        ],
        "values": {},
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk update requires ARMObject object types'
    },
    {
        "description": "Updating with empty objects no values",
        "objects": [],
        "values": {},
        "expected_json": {},
        "expected_params": {'mode': 'query'}
    },
    {
        "description": "Updating with empty objects",
        "objects": [],
        "values": {'name': 'Updated Object'},
        "expected_json": {'name': 'Updated Object'},
        "expected_params": {'mode': 'query'}
    },
    {
        "description": "Updating with incorrect object type",
        "objects": "invalid_object",
        "values": {'test_key': 'test_value'},
        "expected_exception": ValueError,
        "expected_exception_message": 'first parameter must be a list of updates'
    },
    {
        "description": "Updating with invalid objects list",
        "objects": ["invalid_object"],
        "values": {'test_key': 'test_value'},
        "expected_exception": ValueError,
        "expected_exception_message": 'first parameter must be a list of updates'
    },
    {
        "description": "Updating with different object types in bulk",
        "objects": [
            (Transaction(), {'name': 'Updated Object 1'}),
            (Account(), {'name': 'Updated Object 2'})
        ],
        "values": {},
        "expected_exception": TypeError,
        "expected_exception_message": 'Bulk update requires all objects to be of the same type'
    }
])
@patch('payload.arm.request.ARMRequest._request')
def test_armrequest_update(mock_request, test_case, arm_request):
    print(test_case["description"])
    if "expected_exception" in test_case:
        with pytest.raises(test_case["expected_exception"]) as exc_info:
            arm_request.update(objects=test_case["objects"], **test_case["values"])
        assert str(exc_info.value) == test_case["expected_exception_message"]
    else:
        arm_request.update(objects=test_case["objects"], **test_case["values"])
        if test_case.get("expected_params"):
            mock_request.assert_called_once_with(
                'put',
                params=test_case['expected_params'],
                json=test_case["expected_json"])
        else:
            mock_request.assert_called_once_with('put', json=test_case["expected_json"])


# Now use the fixture in your tests
@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_filter_by(arm_request_from_class):
    arm_request_from_class.filter_by(attr="test_attribute", value="test_value")

    assert arm_request_from_class._filters[0].attr == "attr"
    assert arm_request_from_class._filters[0].opval == "test_attribute"
    assert arm_request_from_class._filters[0].val == "test_attribute"

    assert arm_request_from_class._filters[1].attr == "value"
    assert arm_request_from_class._filters[1].opval == "test_value"
    assert arm_request_from_class._filters[1].val == "test_value"


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_all(arm_request_from_class):
    with patch.object(ARMRequest, '_request') as mock_request:
        arm_request_from_class.all()
        mock_request.assert_called_with('get')


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_select(arm_request_from_class):
    with patch.object(ARMRequest, '_request'):
        arm_request_from_class.select('test_field')
        assert arm_request_from_class._attrs == ['test_field']


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_first(arm_request_from_class):
    with patch.object(ARMRequest, '_request') as mock_request:
        mock_request.return_value = [{'field1': 'value1'}, {'field2': 'value2'}]
        result = arm_request_from_class.first()

        mock_request.assert_called_with('get', params={'limit': 1})

        assert result == mock_request.return_value[0]


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_group_by(arm_request_from_class):
    arm_request_from_class.group_by('test_field')
    assert arm_request_from_class._group_by == ['test_field']


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_files(arm_request_from_class, mock_response):
    test_files = {'file': Mock()}

    mock_response.json.return_value = {'object': arm_request_from_class.Object.__spec__['object']}
    mock_response.status_code = 200

    with patch('requests.post', return_value=mock_response) as mock_post:
        arm_request_from_class._request('post', json=test_files)

    assert_mock_get_called_with_correct_values(
        arm_request_from_class, mock_post, expected_files={'file': test_files['file']})


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_id(arm_request_from_class, mock_response):
    test_id = '1'

    mock_response.json.return_value = {'object': arm_request_from_class.Object}
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request_from_class._request('get', id=test_id)

    assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_filters(arm_request_from_class, mock_response):
    test_filters = [
        Attr.filter_attr1 == 'filter_val1',
        Attr.filter_attr2 == 'filter_val2'
    ]

    mock_response.json.return_value = {'object': arm_request_from_class.Object.__spec__['object']}
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request_from_class._filters = test_filters
        arm_request_from_class._request('get')

    assert_mock_get_called_with_correct_values(
        arm_request_from_class,
        mock_get,
        expected_params={'filter_attr1': 'filter_val1', 'filter_attr2': 'filter_val2'})


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_group_by(arm_request_from_class, mock_response):
    test_group_by = ['group1', 'group2']

    mock_response.json.return_value = {'object': arm_request_from_class.Object.__spec__['object']}
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        arm_request_from_class._group_by = test_group_by
        arm_request_from_class._request('get')

    expected_params = {'group_by[0]': 'group1', 'group_by[1]': 'group2'}

    assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get, expected_params=expected_params)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_params(arm_request_from_class, mock_response):
    test_params = {'param1': 'value1'}

    with patch('requests.get') as mock_get:
        mock_response.json.return_value = {'object': arm_request_from_class.Object.__spec__['object']}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        arm_request_from_class._request('get', params=test_params)

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get, expected_params=test_params)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_500_resp_json_not_dict(arm_request_from_class):
    mock_response = Mock(status_code=500, json=lambda: [])

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.UnknownResponse):
            arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_500_no_resp_json_500(arm_request_from_class):
    mock_response = Mock(status_code=500)
    mock_response.json.return_value = {'details': 'test'}

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.InternalServerError):
            arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_unknown_response(arm_request_from_class):
    mock_response = Mock(status_code=999, json=lambda: None)

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.UnknownResponse):
            arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_200_list(arm_request_from_class, mock_response):
    test_list_response = {
        'object': 'list',
        'values': [
            {'id': 1, 'name': 'Test 1'},
            {'id': 2, 'name': 'Test 2'}
        ]
    }

    mock_response.json.return_value = test_list_response
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        result = arm_request_from_class._request('get')

        assert len(result) == len(test_list_response['values'])
        assert result[0]['name'] == test_list_response['values'][0]['name']
        assert result[1]['name'] == test_list_response['values'][1]['name']

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_200_single_obj(arm_request_from_class, mock_response):
    test_object_response = {
        'object': 'single',
        'id': 1,
        'name': 'Test 1'
    }

    mock_response.json.return_value = test_object_response
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        result = arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)
        assert isinstance(result, dict)
        assert result['name'] == 'Test 1'


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_raise_non_500_errors(arm_request_from_class):
    with patch('requests.get',
               return_value=Mock(status_code=400, json=lambda: {'error_type': 'BadRequest'})) as mock_get:
        with pytest.raises(payload.BadRequest):
            arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_raise_bad_request(arm_request_from_class, mock_response):
    mock_response.json.return_value = {}
    mock_response.status_code = 400

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.BadRequest):
            arm_request_from_class._request('get')

    assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_non_matching_error_and_http_code(arm_request_from_class):
    with patch('requests.get',
               return_value=Mock(status_code=400, json=lambda: {'error_type': 'InternalServerError'})) as mock_get:
        with pytest.raises(payload.BadRequest):
            arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_error_name_neq_data_error_type(arm_request_from_class):
    with patch('requests.get',
               return_value=Mock(status_code=500, json=lambda: {'error_type': 'BadRequest'})) as mock_get:
        with pytest.raises(payload.InternalServerError):
            arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_armrequest_request_500_raise_internal_server_error(arm_request_from_class, mock_response):
    mock_response.json.return_value = {}
    mock_response.status_code = 500

    with patch('requests.get', return_value=mock_response) as mock_get:
        with pytest.raises(payload.InternalServerError):
            arm_request_from_class._request('get')

        assert_mock_get_called_with_correct_values(arm_request_from_class, mock_get)


# Test get_object_cls
@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_get_object_cls(arm_object_class):
    item_data = {'object': arm_object_class['object']}
    if 'polymorphic' in arm_object_class:
        item_data.update(arm_object_class['polymorphic'])
    expected = arm_object_class['Object']
    assert get_object_cls(item_data) == expected


# Test nested_qstring_keys
@pytest.mark.parametrize('base, expected', [
    ({'a': {'b': {'c': 1}}}, {'a[b][c]': 1}),
    ({'x': [{'y': 2}, {'z': 3}]}, {'x[0][y]': 2, 'x[1][z]': 3}),
    ({}, {}),
])
def test_nested_qstring_keys(base, expected):
    assert nested_qstring_keys(base) == expected


# Test data2object
@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_data2object(arm_object_class):
    item_data = {'object': arm_object_class['object']}
    if 'polymorphic' in arm_object_class:
        item_data.update(arm_object_class['polymorphic'])
    field_map = set()
    session = None
    expected = arm_object_class['Object'](**item_data) if arm_object_class['Object'] else item_data
    assert data2object(item_data, field_map, session) == expected


# Test convert_fieldmap
@pytest.mark.parametrize('arm_object_class', arm_object_classes)
def test_convert_fieldmap(arm_object_class):
    obj = {'type': arm_object_class['object']}
    field_map = set(arm_object_class.keys()) - {'Object', 'object', 'polymorphic'}
    expected = {arm_object_class['object']: {k: arm_object_class[k] for k in field_map}}
    convert_fieldmap(obj, field_map)
    assert obj == expected


@pytest.mark.parametrize('item, expected', [
    ({
         'object': 'transaction',
         'payment': Payment(amount=100),
         'data': {'list': [1, 2, 3]}
     }, {
         'object': 'transaction',
         'payment': {'type': 'payment', 'amount': 100},
         'data': {'list': [1, 2, 3]}
     }),
    ({
         'object': 'transaction',
         'payment': Payment(),
         'data': {}
     }, {
         'object': 'transaction',
         'payment': {'type': 'payment'},
         'data': {}
     }),
    ({
         'object': 'transaction',
         'payments': [
             Payment(amount=100),
             Payment(amount=200)
         ]
     }, {
         'object': 'transaction',
         'payments': [
             {'type': 'payment', 'amount': 100},
             {'type': 'payment', 'amount': 200}
         ]
     }),
    ({
         'object': 'transaction',
         'payment': {'type': 'payment'}
     }, {
         'object': 'transaction',
         'payment': {'type': 'payment'}
     }),
    ({
         'object': 'transaction',
         'payment': PaymentItem(amount=100),
         'data': {'list': [1, 2, 3]}
     }, {
         'object': 'transaction',
         'payment': {'entry_type': 'payment', 'amount': 100},
         'data': {'list': [1, 2, 3]}
     }),
])
def test_object2data(item, expected):
    assert object2data(item) == expected


@pytest.mark.parametrize('obj, field_map, expected', [
    # Test case 1: Object without 'type' attribute
    ({}, {'field1', 'field2'}, {}),

    # Test case 2: Object with 'type' but field not present
    ({'type': 'payment'}, {'field1', 'field2'}, {'type': 'payment', 'payment': {}}),

    # Test case 3: Object with 'type' and field present
    ({
         'type': 'payment',
         'payment': {},
         'field1': 'value1',
         'field2': 'value2'
     }, {'field1', 'field2'}, {'type': 'payment', 'payment': {'field1': 'value1', 'field2': 'value2'}}),

    # Test case 4: Object with 'type' and field already nested under type
    ({
         'type': 'payment',
         'payment': {'field1': 'value1'}
     }, {'field1'}, {'type': 'payment', 'payment': {'field1': 'value1'}}),

    # Test case 5: Object with 'type' and field already nested under type (field map not in object)
    ({
         'type': 'payment',
         'payment': {'field1': 'value1'}
     }, {'field2'}, {'type': 'payment', 'payment': {'field1': 'value1'}})
])
def test_convert_fieldmap(obj, field_map, expected):
    convert_fieldmap(obj, field_map)
    assert obj == expected


@pytest.mark.parametrize('base, expected', [
    # Test case 1: Empty base
    ({}, {}),

    # Test case 2: Single-level dictionary
    ({'key1': 'value1', 'key2': 'value2'}, {'key1': 'value1', 'key2': 'value2'}),

    # Test case 3: Nested dictionary
    ({'key1': 'value1', 'key2': {'nested1': 'value3', 'nested2': 'value4'}},
     {'key1': 'value1', 'key2[nested1]': 'value3', 'key2[nested2]': 'value4'}),

    # Test case 4: Nested dictionary with empty values
    ({'key1': 'value1', 'key2': {'nested1': '', 'nested2': 'value4'}},
     {'key1': 'value1', 'key2[nested1]': '', 'key2[nested2]': 'value4'}),

    # # Test case 5: Nested dictionary with Attr objects # Fails
    # ({'key1': 'value1', 'key2': {'nested1': Attr, 'nested2': 'value4'}},
    #  {'key1': 'value1', 'key2[nested1]': str(Attr), 'key2[nested2]': 'value4'}),
    # #
    # Test case 6: Nested dictionary with list
    ({'key1': 'value1', 'key2': {'nested1': ['item1', 'item2'], 'nested2': 'value4'}},
     {'key1': 'value1', 'key2[nested1][0]': 'item1', 'key2[nested1][1]': 'item2', 'key2[nested2]': 'value4'}),

    # Test case 7: Nested dictionary with tuple
    ({'key1': 'value1', 'key2': {'nested1': ('item1', 'item2'), 'nested2': 'value4'}},
     {'key1': 'value1', 'key2[nested1][0]': 'item1', 'key2[nested1][1]': 'item2', 'key2[nested2]': 'value4'})
])
def test_nested_qstring_keys(base, expected):
    assert nested_qstring_keys(base) == expected, 'Failed for base: {}'.format(base)


@pytest.mark.parametrize('item, field_map, session, expected', [
    (
            {'field1': 'value1', 'field2': 'value2'},
            {'field1', 'field2'},
            None,
            {'field1': 'value1', 'field2': 'value2'}
    ),
    (
            {'type': 'payment', 'payment': {'field1': 'value1', 'field2': 'value2'}},
            {'field1', 'field2'},
            None,
            {'type': 'payment', 'payment': {'field1': 'value1', 'field2': 'value2'}}
    )
])
def test_data2object(item, field_map, session, expected):
    result = data2object(item, field_map, session)
    assert result == expected
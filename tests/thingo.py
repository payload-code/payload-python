# def setUp(self):
#     self.mock_request = patch.object(ARMRequest, '_request').start()
#     self.request = ARMRequest()
#
# def tearDown(self):
#     patch.stopall()
#
#
# def test_init_with_object_and_session(self):
#     # Mock objects
#     mock_object = Mock()
#     mock_session = Mock()
#
#     # Create ARMRequest instance
#     request = ARMRequest(Object=mock_object, session=mock_session)
#
#     # Assertions
#     self.assertEqual(request.Object, mock_object)
#     self.assertEqual(request.session, mock_session)
#     self.assertEqual(request._filters, [])
#     self.assertEqual(request._attrs, [])
#     self.assertEqual(request._group_by, [])
#
# def test_init_without_object_and_session(self):
#     # Create ARMRequest instance
#     request = ARMRequest()
#
#     # Assertions
#     self.assertIsNone(request.Object)
#     self.assertIsNone(request.session)
#     self.assertEqual(request._filters, [])
#     self.assertEqual(request._attrs, [])
#     self.assertEqual(request._group_by, [])
#
#
# def test_create_single_object(self):
#     # Set up
#     self.mock_request.return_value = Mock(status_code=200, json=Mock(return_value={'id': '123', 'object': 'customer'}))
#
#     # Call create with a single object
#     obj = {'name': 'John', 'age': 30}
#     result = self.request.create(obj)
#
#     # Assertion
#     self.mock_request.assert_called_once_with('post', json={'object': 'customer', 'name': 'John', 'age': 30})
#     self.assertEqual(result, {'id': '123', 'object': 'customer'})
#
# def test_create_single_object_with_object_spec(self):
#     # Set up
#     self.mock_request.return_value = Mock(status_code=200, json=Mock(return_value={'id': '123', 'object': 'customer'}))
#     self.request.Object = Mock(__spec__={'polymorphic': {'type': 'test'}})
#
#     # Call create with a single object
#     obj = {'name': 'John', 'age': 30}
#     result = self.request.create(obj)
#
#     # Assertion
#     self.mock_request.assert_called_once_with('post', json={'object': 'customer', 'name': 'John', 'age': 30, 'type': 'test'})
#     self.assertEqual(result, {'id': '123', 'object': 'customer'})
#
# def test_create_bulk_objects(self):
#     # Set up
#     self.mock_request.return_value = Mock(status_code=200, json=Mock(return_value={'id': '123', 'object': 'customer'}))
#
#     # Call create with a list of objects
#     objects = [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25}]
#     result = self.request.create(objects)
#
#     # Assertion
#     self.mock_request.assert_called_once_with('post', json={'object': 'list', 'values': objects})
#     self.assertEqual(result, {'id': '123', 'object': 'customer'})
#
# def test_create_bulk_objects_with_no_object_type(self):
#     # Call create with a list of objects without specifying object type
#     objects = [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25}]
#     with self.assertRaises(TypeError):
#         self.request.create(objects)
#
# def test_create_bulk_objects_with_different_object_types(self):
#     # Set up
#     self.request.Object = Mock()
#
#     # Call create with a list of objects with different object types
#     objects = [Mock(), Mock()]
#     with self.assertRaises(TypeError):
#         self.request.create(objects)
#
#
# def test_get_with_id(self):
#     # Set up
#     self.mock_request.return_value = Mock(status_code=200, json=Mock(return_value={'id': '123', 'object': 'customer'}))
#
#     # Call get with an id
#     result = self.request.get('123')
#
#     # Assertion
#     self.mock_request.assert_called_once_with('get', id='123', params={})
#     self.assertEqual(result, {'id': '123', 'object': 'customer'})
#
# def test_get_with_id_and_params(self):
#     # Set up
#     self.mock_request.return_value = Mock(status_code=200, json=Mock(return_value={'id': '123', 'object': 'customer'}))
#
#     # Call get with an id and params
#     result = self.request.get('123', param1='value1', param2='value2')
#
#     # Assertion
#     self.mock_request.assert_called_once_with('get', id='123', params={'param1': 'value1', 'param2': 'value2'})
#     self.assertEqual(result, {'id': '123', 'object': 'customer'})
#
# def test_get_with_empty_id(self):
#     # Call get with an empty id
#     with self.assertRaises(ValueError):
#         self.request.get('')
#
#
#
# def test_select(self):
#     # Call select with fields
#     result = self.request.select('field1', 'field2')
#
#     # Assertion
#     self.assertEqual(result, self.request)
#     self.assertEqual(self.request._attrs, ['field1', 'field2'])
#
# def test_group_by(self):
#     # Call group_by with fields
#     result = self.request.group_by('field1', 'field2')
#
#     # Assertion
#     self.assertEqual(result, self.request)
#     self.assertEqual(self.request._group_by, ['field1', 'field2'])
#
#
#
# def test_delete_with_list_of_objects(self):
#     # Create a list of ARMObject instances
#     object1 = ARMObject(id='object1_id')
#     object2 = ARMObject(id='object2_id')
#     objects = [object1, object2]
#
#     # Mock the _request method
#     self.request._request = Mock()
#
#     # Call delete with the list of objects
#     result = self.request.delete(objects)
#
#     # Assertions
#     self.assertEqual(result, self.request)
#     self.request._request.assert_called_once_with('delete', params={'id': 'object1_id|object2_id', 'mode': 'query'})
#
# def test_delete_with_single_object(self):
#     # Create a single ARMObject instance
#     object1 = ARMObject(id='object1_id')
#
#     # Mock the _request method
#     self.request._request = Mock()
#
#     # Call delete with the single object
#     result = self.request.delete(object1)
#
#     # Assertions
#     self.assertEqual(result, self.request)
#     self.request._request.assert_called_once_with('delete', id='object1_id')
#
# def test_delete_with_filters(self):
#     # Set filters and Object attribute
#     self.request._filters = {'field': 'value'}
#     self.request.Object = ARMObject
#
#     # Mock the _request method
#     self.request._request = Mock()
#
#     # Call delete without specifying objects
#     result = self.request.delete()
#
#     # Assertions
#     self.assertEqual(result, self.request)
#     self.request._request.assert_called_once_with('delete', params={'mode': 'query'})
#
# def test_delete_with_invalid_input(self):
#     # Call delete with invalid input
#     with self.assertRaises(TypeError):
#         self.request.delete("invalid_input")
#
#
#
# def test_update_with_list_of_objects(self):
#     # Create a list of updates (object, values)
#     object1 = ARMObject(id='object1_id')
#     object2 = ARMObject(id='object2_id')
#     updates = [(object1, {'field': 'value'}), (object2, {'field': 'value'})]
#
#     # Mock the _request method
#     self.request._request = Mock()
#
#     # Call update with the list of objects and values
#     result = self.request.update(objects=updates)
#
#     # Assertions
#     self.assertEqual(result, self.request)
#     expected_updates = {
#         'object': 'list',
#         'values': [{'id': 'object1_id', 'field': 'value'}, {'id': 'object2_id', 'field': 'value'}]
#     }
#     self.request._request.assert_called_once_with('put', json=expected_updates)
#
# def test_update_with_query_params(self):
#     # Mock the _request method
#     self.request._request = Mock()
#
#     # Call update with query parameters
#     result = self.request.update(field='value')
#
#     # Assertions
#     self.assertEqual(result, self.request)
#     self.request._request.assert_called_once_with('put', params={'mode': 'query'}, json={'field': 'value'})
#
# def test_update_with_invalid_input(self):
#     # Call update with invalid input
#     with self.assertRaises(ValueError):
#         self.request.update("invalid_input")
#
# def test_update_with_empty_list(self):
#     # Call update with an empty list
#     with self.assertRaises(ValueError):
#         self.request.update([])
#
# def test_update_with_inconsistent_object_types(self):
#     # Create objects with different types
#     object1 = ARMObject(id='object1_id')
#     object2 = ARMObject(id='object2_id', type='different_type')
#     updates = [(object1, {'field': 'value'}), (object2, {'field': 'value'})]
#
#     # Call update with inconsistent object types
#     with self.assertRaises(TypeError):
#         self.request.update(objects=updates)
#
#
# def test_filter_by_with_filters(self):
#     # Mock the nested_qstring_keys function
#     with patch('payload.arm.request.nested_qstring_keys', return_value={'field': 'value'}) as mock_nested_qstring_keys:
#         # Call filter_by with filters
#         result = self.request.filter_by('filter1', 'filter2', key1='value1', key2='value2')
#
#         # Assertions
#         self.assertEqual(result, self.request)
#         self.assertEqual(self.request._filters, ['filter1', 'filter2', Attr.key1 == 'value1', Attr.key2 == 'value2'])
#         mock_nested_qstring_keys.assert_called_once_with({'key1': 'value1', 'key2': 'value2'})
#
# def test_all(self):
#     # Mock the _request method
#     self.request._request = Mock(return_value=[{'id': 'object1_id'}, {'id': 'object2_id'}])
#
#     # Call all
#     result = self.request.all()
#
#     # Assertions
#     self.assertEqual(result, [{'id': 'object1_id'}, {'id': 'object2_id'}])
#     self.request._request.assert_called_once_with('get')
#
# def test_first_with_results(self):
#     # Mock the _request method
#     self.request._request = Mock(return_value=[{'id': 'object1_id'}, {'id': 'object2_id'}])
#
#     # Call first
#     result = self.request.first()
#
#     # Assertions
#     self.assertEqual(result, {'id': 'object1_id'})
#     self.request._request.assert_called_once_with('get', params={'limit': 1})
#
# def test_first_without_results(self):
#     # Mock the _request method
#     self.request._request = Mock(return_value=[])
#
#     # Call first
#     result = self.request.first()
#
#     # Assertions
#     self.assertIsNone(result)
#     self.request._request.assert_called_once_with('get', params={'limit': 1})
#
#
# def test_request_with_json(self, mock_nested_qstring_keys, mock_convert_fieldmap):
#     # Set up
#     method = 'post'
#     id = None
#     headers = {}
#     params = {}
#     json_data = {'name': 'John', 'age': 30}
#
#     # Mock response
#     response_mock = Mock(
#         status_code=200,
#         json=Mock(return_value={'id': '123', 'name': 'John'})
#     )
#
#     # Patch the requests module and mock the response
#     with patch('requests.post', return_value=response_mock) as mock_post_request:
#         # Mock nested_qstring_keys
#         mock_nested_qstring_keys.return_value = {'name': 'John', 'age': 30}
#
#         # Make the request
#         result = self.request._request(method, id=id, headers=headers, params=params, json=json_data)
#
#         # Assertions
#         mock_post_request.assert_called_once_with(
#             self.session_mock.api_url + '/' + self.object_mock.endpoint,
#             headers=headers,
#             params=params,
#             auth=(self.session_mock.api_key, ''),
#             json=json_data
#         )
#         self.assertEqual(result, {'id': '123', 'name': 'John'})
#
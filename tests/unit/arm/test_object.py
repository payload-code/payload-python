from unittest.mock import Mock

import pytest

from payload.arm.object import ARMObject, ARMObjectWrapper


class MockARMObject(ARMObject):
    """Mock ARMObject for testing"""

    __spec__ = {'object': 'mock_object', 'endpoint': '/mocks'}


class TestARMObjectWrapperIter:
    """Unit tests for ARMObjectWrapper.__iter__ method"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing"""
        return Mock(api_key='test_key', api_url='https://api.test.com')

    @pytest.fixture
    def wrapper(self, mock_session):
        """Create an ARMObjectWrapper instance for testing"""
        return ARMObjectWrapper(MockARMObject, mock_session)

    def test_iter_unpacking_equals_asterisk(self, wrapper):
        """Test that unpacking ARMObjectWrapper with * operator yields '*'"""
        result = [*wrapper]

        assert result == ['*']

    def test_iter_single_unpack_equals_asterisk(self, wrapper):
        """Test that single unpacking ARMObjectWrapper equals '*'"""
        (item,) = wrapper

        assert item == '*'

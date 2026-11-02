import json
from unittest.mock import Mock

import pytest

import payload

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


@pytest.mark.parametrize('serialize', ['data', 'json'])
def test_serializing_payment_preserves_nested_models(serialize):
    card = payload.Card(expiry='12/28')
    payment = payload.Payment(amount=100, payment_method=card)
    expected = {
        'type': 'payment',
        'amount': 100,
        'payment_method': {'type': 'card', 'card': {'expiry': '12/28'}},
    }

    serialized = getattr(payment, serialize)()
    assert (json.loads(serialized) if serialize == 'json' else serialized) == expected
    assert payment.payment_method is card
    assert payment.payment_method.expiry == '12/28'
    assert payment.data() == expected


@pytest.mark.parametrize('serialize', ['data', 'json'])
def test_serializing_invoice_preserves_item_models(serialize):
    charge = payload.ChargeItem(amount=29.99)
    invoice = payload.Invoice(items=[charge])
    items = invoice.items
    expected = {'items': [{'entry_type': 'charge', 'amount': 29.99}]}

    serialized = getattr(invoice, serialize)()
    assert (json.loads(serialized) if serialize == 'json' else serialized) == expected
    assert invoice.items is items
    assert invoice.items[0] is charge
    assert invoice.items[0].amount == 29.99
    assert invoice.data() == expected

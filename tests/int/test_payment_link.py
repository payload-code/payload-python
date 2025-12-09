import pytest

import payload as pl

from .fixtures import Fixtures
from payload.exceptions import NotFound


class TestPaymentLink(Fixtures):
    def test_create_payment_link_one_time(self, api_key, processing_account):
        payment_link = pl.PaymentLink.create(
            type="one_time",
            description="Payment Request",
            amount=10.00,
            processing_id=processing_account.id,
        )

        assert payment_link.processing_id == processing_account.id
        assert payment_link.type == 'one_time'


    def test_create_payment_link_reusable(self, api_key, processing_account):
        payment_link = pl.PaymentLink.create(
            type="reusable",
            description="Payment Request",
            amount=10.00,
            processing_id=processing_account.id,
        )

        assert payment_link.processing_id == processing_account.id
        assert payment_link.type == 'reusable'


    def test_delete_payment_link_reusable(self, payment_link_reusable):
        with pytest.raises(NotFound):
            payment_link_reusable.delete()
            payment_link_reusable_get = pl.PaymentLink.get(payment_link_reusable.id)


    def test_delete_payment_link_one_time(self, payment_link_one_time):
        with pytest.raises(NotFound):
            payment_link_one_time.delete()
            payment_link_one_time_get = pl.PaymentLink.get(payment_link_one_time.id)
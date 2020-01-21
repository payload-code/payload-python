import pytest

import payload as pl

from .fixtures import Fixtures


class TestPaymentLink(Fixtures):
    def test_create_payment_link(self, api_key, processing_account):
        payment_link = pl.PaymentLink.create(
            type="one_time",
            description="Payment Request",
            amount=10.00,
            processing_id=processing_account.id,
        )

        assert payment_link.processing_id == processing_account.id

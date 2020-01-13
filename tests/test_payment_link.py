import pytest

import payload as pl

from .fixtures import Fixtures

pl.api_key = "your_secret_key_3bzs0Ilz3X8TsM76hFOxT"


class TestPaymentLink(Fixtures):
    def test_create_payment_link(self, processing_account):
        payment_link = pl.PaymentLink.create(
            type="one_time",
            description="Payment Request",
            amount=10.00,
            processing_id=processing_account.id,
        )

        assert payment_link.processing_id == processing_account.id

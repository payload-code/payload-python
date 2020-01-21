import random
import string

import pytest

import payload as pl
from payload.exceptions import BadRequest

from .fixtures import Fixtures


class TestPaymentMethod(Fixtures):
    def test_create_payment_card(self, api_key, card_payment):
        assert card_payment.status == "processed"

    def test_create_payment_bank(self, api_key, bank_payment):
        assert bank_payment.status == "processed"

    def test_payment_filters(self, api_key):
        letters = string.ascii_lowercase
        rand_description = "".join(random.choice(letters) for i in range(10))

        card_payment = pl.Payment.create(
            amount=100.0,
            description=rand_description,
            payment_method=pl.Card(
                card_number="4242 4242 4242 4242", expiry="05/22", card_code="123"
            ),
        )

        payments = pl.Payment.filter_by(
            pl.attr.amount > 99,
            pl.attr.amount < (200),
            pl.attr.description.contains(rand_description),
            pl.attr.created_at > ("2019-12-31"),
        ).all()

        assert len(payments) == 1
        assert payments[0].id == card_payment.id

    def test_void_card_payment(self, api_key, card_payment):
        card_payment.update(status="voided")

        assert card_payment.status == "voided"

    def test_void_bank_payment(self, api_key, bank_payment):
        bank_payment.update(status="voided")

        assert bank_payment.status == "voided"

    def test_refund_card_payment(self, api_key, card_payment):

        refund = pl.Refund.create(
            amount=100, ledger=[pl.Ledger(assoc_transaction_id=card_payment.id)]
        )

        assert refund.type == "refund"
        assert refund.amount == 100
        assert refund.status_code == "approved"

    def test_partial_refund_card_payment(self, api_key, card_payment):

        refund = pl.Refund.create(
            amount=10, ledger=[pl.Ledger(assoc_transaction_id=card_payment.id)]
        )

        assert refund.type == "refund"
        assert refund.amount == 10
        assert refund.status_code == "approved"

    def test_blind_refund_card_payment(self, api_key, processing_account):
        refund = pl.Refund.create(
            amount=10,
            processing_id=processing_account.id,
            payment_method=pl.Card(card_number="4242 4242 4242 4242"),
        )

        assert refund.type == "refund"
        assert refund.amount == 10
        assert refund.status_code == "approved"

    def test_refund_bank_payment(self, api_key, bank_payment):
        refund = pl.Refund.create(
            amount=100, ledger=[pl.Ledger(assoc_transaction_id=bank_payment.id)]
        )

        assert refund.type == "refund"
        assert refund.amount == bank_payment.amount
        assert refund.status_code == "approved"

    def test_partial_refund_bank_payment(self, api_key, bank_payment):
        refund = pl.Refund.create(
            amount=10, ledger=[pl.Ledger(assoc_transaction_id=bank_payment.id)]
        )

        assert refund.type == "refund"
        assert refund.amount == 10
        assert refund.status_code == "approved"

    def test_convenience_fee(self, api_key):
        payment = pl.Payment.select("*", "conv_fee").create(
            amount=100, payment_method=pl.Card(card_number="4242 4242 4242 4242")
        )

        assert payment.fee
        assert payment.conv_fee != None

    def test_invalid_payment_method_type_invalid_attributes(self, api_key):
        with pytest.raises(BadRequest):
            pl.Transaction.create(type="invalid", card_number="4242 4242 4242 4242")

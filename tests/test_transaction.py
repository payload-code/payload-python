import pytest

import payload as pl
from payload.exceptions import NotFound

from .fixtures import Fixtures

pl.api_key = "your_secret_key_3bzs0Ilz3X8TsM76hFOxT"


class TestTransaction(Fixtures):
    def test_transaction_ledger_empty(self, card_payment):
        transaction = pl.Transaction.select("*", "ledger").get(card_payment.id)

        assert transaction.ledger == []

    def test_unified_payout_batching(self, processing_account):
        pl.Refund.create(
            amount=10,
            processing_id=processing_account.id,
            payment_method=pl.Card(card_number="4242 4242 4242 4242"),
        )

        transactions = (
            pl.Transaction.select("*", "ledger")
            .filter_by(type="refund", processing_id=processing_account.id)
            .all()
        )

        assert len(transactions) == 1
        assert transactions[0].processing_id == processing_account.id

    def test_get_transactions(self, card_payment):
        payments = pl.Transaction.filter_by(status="processed", type="payment").all()
        assert len(payments) > 0

    def test_risk_flag(self, card_payment):
        assert card_payment.risk_flag == "allowed"

    def test_update_processed(self, card_payment):
        card_payment.update(status="voided")
        assert card_payment.status == "voided"

    def test_transactions_not_found(self, card_payment):
        with pytest.raises(NotFound):
            pl.Transaction.get("invalid")

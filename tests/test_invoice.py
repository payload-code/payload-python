import datetime

import pytest

import payload as pl

from .fixtures import Fixtures
from payload.exceptions import NotFound



@pytest.fixture
def invoice(processing_account, customer_account):
    invoice = pl.Invoice.create(
        type="bill",
        processing_id=processing_account.id,
        due_date=datetime.datetime.today().strftime('%Y-%m-%d'),
        customer_id=customer_account.id,
        items=[pl.ChargeItem(amount=29.99)],
    )

    return invoice


class TestInvoice(Fixtures):
    def test_create_invoice(self, invoice):
        assert invoice.due_date == datetime.datetime.today().strftime('%Y-%m-%d')
        assert invoice.status == "unpaid"

    def test_pay_invoice(self, invoice, customer_account):
        assert invoice.due_date == datetime.datetime.today().strftime('%Y-%m-%d')
        assert invoice.status == "unpaid"

        card_payment = pl.Card.create(
            account_id=customer_account.id, card_number="4242 4242 4242 4242", expiry='12/35', card_code='123'
        )

        if invoice.status != "paid":
            pl.Payment.create(
                amount=invoice.amount_due,
                customer_id=customer_account.id,
                payment_method_id=card_payment.id,
                allocations=[pl.PaymentItem(invoice_id=invoice.id)],
            )

        get_invoice = pl.Invoice.get(invoice.id)
        assert get_invoice.status == "paid"

    def test_delete_invoice(self, invoice):
        with pytest.raises(NotFound):
            invoice.delete()
            invoice_get = pl.Invoice.get(invoice.id)
import os
import payload as pl
import pytest


class Fixtures(object):
    @pytest.fixture
    def api_key(self):
        pl.api_key = os.environ["TEST_SECRET_KEY"]

    @pytest.fixture
    def customer_account(self):
        customer_account = pl.Customer.create(name="Test", email="test@example.com")
        return customer_account

    @pytest.fixture
    def processing_account(self):
        processing_account = pl.ProcessingAccount.create(
            {
                "name": "Processing Account",
                "payment_methods": {
                    "type": "bank_account",
                    "bank_account": {
                        "account_number": "123456789",
                        "routing_number": "036001808",
                        "account_type": "checking",
                    },
                    "legal_entity": {
                        "legal_name": "Test",
                        "type": "INDIVIDUAL_SOLE_PROPRIETORSHIP",
                        "ein": "23 423 4234",
                        "street_address": "123 Example Street",
                        "unit_number": "Suite 1",
                        "city": "New York",
                        "state_province": "NY",
                        "state_incorporated": "NY",
                        "postal_code": "11238",
                        "phone_number": "(111) 222-3333",
                        "website": "www.payload.co",
                        "start_date": "05/01/2015",
                        "contact_name": "Test Person",
                        "contact_email": "test.person@example.com",
                        "contact_title": "VP",
                        "owners": [
                            {
                                "full_name": "Test Person",
                                "email": "test.person@example.com",
                                "ssn": "234 23 4234",
                                "birth_date": "06/20/1985",
                                "title": "CEO",
                                "ownership": "100",
                                "street_address": "123 Main Street",
                                "unit_number": "#1A",
                                "city": "New York",
                                "state_province": "NY",
                                "postal_code": "10001",
                                "phone_number": "(111) 222-3333",
                                "type": "owner",
                            }
                        ],
                    },
                },
            }
        )
        return processing_account

    @pytest.fixture
    def card_payment(self):
        card_payment = pl.Payment.create(
            amount=100.0, payment_method=pl.Card(card_number="4242 4242 4242 4242")
        )
        return card_payment

    @pytest.fixture
    def bank_payment(self, processing_account):

        bank_payment = pl.Payment.create(
            type="payment",
            amount=100.0,
            payment_method=pl.BankAccount(
                account_number="1234567890",
                routing_number="021000121",
                account_type="checking",
            ),
        )

        return bank_payment

import datetime
import os
import random

import pytest

import payload as pl


class Fixtures(object):
    @pytest.fixture(scope='session', autouse=True)
    def api_key(self):
        pl.api_key = os.environ['TEST_SECRET_KEY']
        if 'TEST_API_URL' in os.environ:
            pl.api_url = os.environ['TEST_API_URL']

    @pytest.fixture
    def customer_account(self):
        customer_account = pl.Customer.create(name='Test', email='test@example.com')
        return customer_account

    @pytest.fixture
    def processing_account(self):
        processing_account = pl.ProcessingAccount.create(
            {
                'name': 'Processing Account',
                'legal_entity': {
                    'legal_name': 'Test',
                    'type': 'INDIVIDUAL_SOLE_PROPRIETORSHIP',
                    'ein': '23 423 4234',
                    'street_address': '123 Example Street',
                    'unit_number': 'Suite 1',
                    'city': 'New York',
                    'state_province': 'NY',
                    'state_incorporated': 'NY',
                    'postal_code': '11238',
                    'country': 'US',
                    'phone_number': '(111) 222-3333',
                    'website': 'http://www.payload.com',
                    'start_date': '05/01/2015',
                    'contact_name': 'Test Person',
                    'contact_email': 'test.person@example.com',
                    'contact_title': 'VP',
                    'owners': [
                        {
                            'full_name': 'Test Person',
                            'email': 'test.person@example.com',
                            'ssn': '234 23 4234',
                            'birth_date': '06/20/1985',
                            'title': 'CEO',
                            'ownership': '100',
                            'street_address': '123 Main Street',
                            'unit_number': '#1A',
                            'city': 'New York',
                            'state_province': 'NY',
                            'postal_code': '10001',
                            'phone_number': '(111) 222-3333',
                            'type': 'owner',
                        }
                    ],
                },
                'payment_methods': {
                    'type': 'bank_account',
                    'bank_account': {
                        'account_number': '123456789',
                        'routing_number': '036001808',
                        'account_type': 'checking',
                    },
                },
            }
        )
        return processing_account

    @pytest.fixture
    def card_payment(self, processing_account):
        card_payment = pl.Payment.create(
            processing_id=processing_account.id,
            amount=random.random() * 100,
            payment_method=pl.Card(
                card_number='4242 4242 4242 4242',
                expiry='12/35',
                billing_address=dict(postal_code='11111'),
            ),
        )
        return card_payment

    @pytest.fixture
    def bank_payment(self):
        bank_payment = pl.Payment.create(
            type='payment',
            amount=random.random() * 1000,
            payment_method=pl.BankAccount(
                account_number='1234567890',
                routing_number='036001808',
                account_type='checking',
            ),
        )

        return bank_payment

    @pytest.fixture
    def bank_payment_method(self):
        bank_payment = pl.Payment.create(
            type='payment',
            amount=random.random() * 100,
            payment_method=pl.BankAccount(
                account_number='1234567890',
                routing_number='036001808',
                account_type='checking',
            ),
        )

        return bank_payment

    @pytest.fixture
    def payment_link_one_time(self, processing_account):
        payment_link = pl.PaymentLink.create(
            type='one_time',
            description='Payment Request',
            amount=10.00,
            processing_id=processing_account.id,
        )

        return payment_link

    @pytest.fixture
    def payment_link_reusable(self, processing_account):
        payment_link = pl.PaymentLink.create(
            type='reusable',
            description='Payment Request',
            amount=10.00,
            processing_id=processing_account.id,
        )

        return payment_link

    @pytest.fixture
    def invoice(self, processing_account, customer_account):
        invoice = pl.Invoice.create(
            type='bill',
            processing_id=processing_account.id,
            due_date=datetime.datetime.today().strftime('%Y-%m-%d'),
            customer_id=customer_account.id,
            items=[pl.ChargeItem(amount=29.99)],
        )

        return invoice

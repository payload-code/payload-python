import random
import string

import pytest

import payload as pl
from payload.exceptions import NotFound

from .fixtures import Fixtures

pl.api_key = "your_secret_key_3bzs0Ilz3X8TsM76hFOxT"


class TestAccount(Fixtures):
    def test_create_customer_account(self):
        customer_account = pl.Customer.create(name="Test", email="test@example.com")

        assert customer_account.id

    def test_delete(self, customer_account):
        with pytest.raises(NotFound):
            customer_account.delete()
            customer_get = pl.Customer.get(customer_account.id)

    def test_create_mult_accounts(self):
        letters = string.ascii_lowercase
        rand_email1 = "".join(random.choice(letters) for i in range(5)) + "@example.com"
        rand_email2 = "".join(random.choice(letters) for i in range(5)) + "@example.com"

        accounts = pl.create(
            [
                pl.Customer(email=rand_email1, name="Matt Perez"),
                pl.Customer(email=rand_email2, name="Andrea Kearney"),
            ]
        )

        get_account_1 = pl.Account.filter_by(email=rand_email1).all()[0]
        get_account_2 = pl.Account.filter_by(email=rand_email2).all()[0]

        assert get_account_1
        assert get_account_2

    def test_get_processing_account(self, processing_account):
        assert pl.ProcessingAccount.get(processing_account.id)
        assert processing_account.processing["status"] == "pending"

    def test_paging_and_ordering_results(self):
        accounts = pl.create(
            [
                pl.Customer(email="account1@example.com", name="Randy Robson"),
                pl.Customer(email="account2@example.com", name="Brandy Bobson"),
                pl.Customer(email="account3@example.com", name="Mandy Johnson"),
            ]
        )

        customers = pl.Customer.filter_by(
            order_by="created_at", limit=3, offset=1
        ).all()

        assert len(customers) == 3
        assert customers[0].created_at < customers[1].created_at
        assert customers[1].created_at < customers[2].created_at

    def test_update_cust(self, customer_account):
        customer_account.update(email="test2@example.com")
        assert customer_account.email == "test2@example.com"

    def test_get_cust(self, customer_account):
        assert pl.Customer.get(customer_account.id)

    def test_select_cust_attr(self, customer_account):
        select_customer_id = pl.Customer.select("id").get(customer_account.id).get("id")
        assert select_customer_id == customer_account.id

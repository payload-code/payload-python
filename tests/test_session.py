import pytest
import os
import string
import random

import payload
from payload.exceptions import BadRequest, NotFound

from .fixtures import Fixtures

import dateutil.parser


@pytest.fixture
def pl():
    payload.api_key = None
    pl = payload.Session(os.environ["TEST_SECRET_KEY"])
    if "TEST_API_URL" in os.environ:
        pl.api_url = os.environ["TEST_API_URL"]

    return pl


class TestSession(Fixtures):
    def test_create_customer_account(self, pl):
        customer_account = pl.Customer.create(name="Test", email="test@example.com")
        assert customer_account.id

    def test_delete(self, pl):
        customer_account = pl.Customer.create(name="Test", email="test@example.com")
        with pytest.raises(NotFound):
            customer_account.delete()
            customer_get = pl.Customer.get(customer_account.id)

    def test_create_mult_accounts(self, pl):
        letters = string.ascii_lowercase
        rand_email1 = "".join(random.choice(letters) for i in range(5)) + "@example.com"
        rand_email2 = "".join(random.choice(letters) for i in range(5)) + "@example.com"

        accounts = pl.create(
            [
                pl.Customer(email=rand_email1, name="Matt Perez"),
                pl.Customer(email=rand_email2, name="Andrea Kearney"),
            ]
        )

        get_account_1 = pl.Customer.filter_by(email=rand_email1).all()[0]
        get_account_2 = pl.Customer.filter_by(email=rand_email2).all()[0]

        assert get_account_1
        assert get_account_2

    def test_paging_and_ordering_results(self, pl):
        accounts = pl.create(
            [
                pl.Customer(email="account1@example.com", name="Randy Robson"),
                pl.Customer(email="account2@example.com", name="Brandy Bobson"),
                pl.Customer(email="account3@example.com", name="Mandy Johnson"),
            ]
        )

        customers = pl.Customer.filter_by(order_by="created_at", limit=3, offset=1).all()

        assert len(customers) == 3
        assert dateutil.parser.parse(customers[0].created_at) <= dateutil.parser.parse(
            customers[1].created_at
        )
        assert dateutil.parser.parse(customers[1].created_at) <= dateutil.parser.parse(
            customers[2].created_at
        )

    def test_update_cust(self, pl):
        customer_account = pl.Customer.create(name="Test", email="test@example.com")
        customer_account.update(email="test2@example.com")

        assert customer_account.email == "test2@example.com"

    def test_update_mult_acc(self, pl):
        customer_account_1 = pl.Customer.create(name="Brandy", email="test1@example.com")
        customer_account_2 = pl.Customer.create(name="Sandy", email="test2@example.com")

        pl.update(
            [
                [customer_account_1, {"email": "brandy@example.com"}],
                [customer_account_2, {"email": "sandy@example.com"}],
            ]
        )

        assert customer_account_1.email == "brandy@example.com"
        assert customer_account_2.email == "sandy@example.com"

    def test_get_cust(self, pl):
        customer_account = pl.Customer.create(name="Test", email="test@example.com")
        assert pl.Customer.get(customer_account.id)

    def test_select_cust_attr(self, pl):
        customer_account = pl.Customer.create(name="Test", email="test@example.com")
        select_customer_id = pl.Customer.select("id").get(customer_account.id).get("id")
        assert select_customer_id == customer_account.id

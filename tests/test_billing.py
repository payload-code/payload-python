import pytest

import payload as pl

from .fixtures import Fixtures


@pytest.fixture()
def billing_schedule(processing_account, customer_account):
    billing_schedule = pl.BillingSchedule.create(
        start_date="2019-01-01",
        end_date="2019-12-31",
        recurring_frequency="monthly",
        type="subscription",
        customer_id=customer_account.id,
        processing_id=processing_account.id,
        charges=pl.BillingCharge(type="option_1", amount=39.99),
    )

    return billing_schedule


class TestBilling(Fixtures):
    def test_create_billing_schedule(
        self, api_key, billing_schedule, processing_account
    ):
        assert billing_schedule.processing_id == processing_account.id
        assert billing_schedule.charges[0].amount == 39.99

    def test_update_billing_schedule_frequency(
        self, api_key, billing_schedule, processing_account
    ):
        assert billing_schedule.processing_id == processing_account.id
        assert billing_schedule.charges[0].amount == 39.99

        billing_schedule.update(recurring_frequency="quarterly")

        assert billing_schedule.recurring_frequency == "quarterly"

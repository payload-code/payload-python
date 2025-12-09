"""
Payload python library
------------------------

Documentation: https://docs.payload.com

:copyright: (c) 2025 Payload (http://payload.com)
:license: MIT License
"""

__all__ = [
    # Version
    '__version__',
    # ARM
    'ARMRequest',
    'attr',
    'session_factory',
    'Session',
    # Functions
    'create',
    'update',
    'delete',
    # Module variables
    'URL',
    'api_key',
    'api_url',
    'api_version',
    # Submodules
    'objects',
    # Exceptions
    'BadRequest',
    'Forbidden',
    'InternalServerError',
    'InvalidAttributes',
    'NotFound',
    'PayloadError',
    'ServiceUnavailable',
    'TooManyRequests',
    'TransactionDeclined',
    'Unauthorized',
    'UnknownResponse',
    # Objects
    'AccessToken',
    'Account',
    'BankAccount',
    'BillingCharge',
    'BillingSchedule',
    'Card',
    'ChargeItem',
    'ClientToken',
    'Credit',
    'Customer',
    'Deposit',
    'Invoice',
    'Ledger',
    'LineItem',
    'OAuthToken',
    'Org',
    'Payment',
    'PaymentActivation',
    'PaymentItem',
    'PaymentLink',
    'PaymentMethod',
    'ProcessingAccount',
    'Refund',
    'Transaction',
    'User',
    'Webhook',
]

from . import objects
from .arm import ARMRequest
from .arm import Attr as attr
from .arm import session_factory
from .exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
    InvalidAttributes,
    NotFound,
    PayloadError,
    ServiceUnavailable,
    TooManyRequests,
    TransactionDeclined,
    Unauthorized,
    UnknownResponse,
)
from .objects import (
    AccessToken,
    Account,
    BankAccount,
    BillingCharge,
    BillingSchedule,
    Card,
    ChargeItem,
    ClientToken,
    Credit,
    Customer,
    Deposit,
    Invoice,
    Ledger,
    LineItem,
    OAuthToken,
    Org,
    Payment,
    PaymentActivation,
    PaymentItem,
    PaymentLink,
    PaymentMethod,
    ProcessingAccount,
    Refund,
    Transaction,
    User,
    Webhook,
)
from .version import __version__

URL = 'https://api.payload.com'

api_key = None
api_url = URL
api_version = None

Session = session_factory('PayloadSession', objects)


def create(*args, **kwargs):
    return ARMRequest().create(*args, **kwargs)


def update(*args, **kwargs):
    return ARMRequest().update(*args, **kwargs)


def delete(*args, **kwargs):
    return ARMRequest().delete(*args, **kwargs)

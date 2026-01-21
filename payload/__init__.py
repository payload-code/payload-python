"""
Payload python library
------------------------

Documentation: https://docs.payload.com

:copyright: (c) 2026 Payload (http://payload.com)
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
    'ProcessingRule',
    'Refund',
    'Transaction',
    'User',
    'Webhook',
    # New API v2 Objects
    'Profile',
    'BillingItem',
    'Intent',
    'InvoiceItem',
    'PaymentAllocation',
    'Entity',
    'Stakeholder',
    'ProcessingAgreement',
    'Transfer',
    'TransactionOperation',
    'CheckFront',
    'CheckBack',
    'ProcessingSettings',
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
from .objects import (  # API v2 Objects
    AccessToken,
    Account,
    BankAccount,
    BillingCharge,
    BillingItem,
    BillingSchedule,
    Card,
    ChargeItem,
    CheckBack,
    CheckFront,
    ClientToken,
    Credit,
    Customer,
    Deposit,
    Entity,
    Intent,
    Invoice,
    InvoiceItem,
    Ledger,
    LineItem,
    OAuthToken,
    Org,
    Payment,
    PaymentActivation,
    PaymentAllocation,
    PaymentItem,
    PaymentLink,
    PaymentMethod,
    ProcessingAccount,
    ProcessingAgreement,
    ProcessingRule,
    ProcessingSettings,
    Profile,
    Refund,
    Stakeholder,
    Transaction,
    TransactionOperation,
    Transfer,
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

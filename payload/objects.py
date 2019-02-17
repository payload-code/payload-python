from .arm.object import ARMObject

class Account(ARMObject):
    __spec__ = { 'object': 'account' }

class Customer(Account):
    __spec__ = { 'polymorphic': { 'type': 'customer' } }

class ProcessingAccount(Account):
    __spec__ = { 'polymorphic': { 'type':'processing'} }

class Org(ARMObject):
    __spec__ = { 'endpoint': '/accounts/orgs', 'object': 'org' }

class User(ARMObject):
    __spec__ = { 'object': 'user' }

class Transaction(ARMObject):
    __spec__ = { 'object': 'transaction' }

class Payment(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'payment' } }

class Refund(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'refund' } }

class PaymentMethod(ARMObject):
    __spec__ = { 'object': 'payment_method' }

class Card(PaymentMethod):
    __spec__ = { 'polymorphic': { 'type': 'card' } }

class BankAccount(PaymentMethod):
    __spec__ = { 'polymorphic': { 'type': 'bank_account' } }

class Event(ARMObject):
    __spec__ = { 'object': 'event' }

class BillingSchedule(ARMObject):
    __spec__ = { 'object': 'billing_schedule' }

class BillingCharge(ARMObject):
    __spec__ = { 'object': 'billing_charge' }

class Invoice(ARMObject):
    __spec__ = { 'object': 'invoice' }

class LineItem(ARMObject):
    __spec__ = { 'object': 'line_items' }

class ChargeItem(LineItem):
    __spec__ = { 'polymorphic': { 'type': 'charge' } }

class PaymentItem(LineItem):
    __spec__ = { 'polymorphic': { 'type': 'payment' } }

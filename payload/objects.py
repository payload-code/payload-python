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

    def void(self):
        self.update(status='voided')
        return self

class Payment(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'payment' } }

class Refund(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'refund' } }

class Deposit(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'deposit' } }

class Ledger(ARMObject):
    __spec__ = { 'object': 'transaction_ledger' }

class PaymentMethod(ARMObject):
    __spec__ = { 'object': 'payment_method' }

class Card(PaymentMethod):
    __spec__ = { 'polymorphic': { 'type': 'card' } }
    field_map = set(['card_number', 'expiry'])

class BankAccount(PaymentMethod):
    __spec__ = { 'polymorphic': { 'type': 'bank_account' } }

class BillingSchedule(ARMObject):
    __spec__ = { 'object': 'billing_schedule' }

class BillingCharge(ARMObject):
    __spec__ = { 'object': 'billing_charge' }

class Invoice(ARMObject):
    __spec__ = { 'object': 'invoice' }

class LineItem(ARMObject):
    __spec__ = { 'object': 'line_item' }

class ChargeItem(LineItem):
    __spec__ = { 'polymorphic': { 'type': 'charge' } }

class PaymentItem(LineItem):
    __spec__ = { 'polymorphic': { 'type': 'payment' } }

class Webhook(ARMObject):
    __spec__ = { 'object': 'webhook' }

class PaymentLink(ARMObject):
    __spec__ = { 'object': 'payment_link' }

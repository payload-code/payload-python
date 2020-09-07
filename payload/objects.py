from .arm.object import ARMObject

class Account(ARMObject):
    __spec__ = { 'object': 'account' }

class Customer(ARMObject):
    __spec__ = { 'object': 'customer' }

class ProcessingAccount(ARMObject):
    __spec__ = { 'object': 'processing_account' }

class Org(ARMObject):
    __spec__ = { 'endpoint': '/accounts/orgs', 'object': 'org' }

class User(ARMObject):
    __spec__ = { 'object': 'user' }

class Transaction(ARMObject):
    __spec__ = { 'endpoint': '/transactions', 'object': 'transaction' }

    def void(self):
        self.update(status='voided')
        return self

class Payment(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'payment' } }

class Refund(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'refund' } }

class Credit(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'credit' } }

class Deposit(Transaction):
    __spec__ = { 'polymorphic': { 'type': 'deposit' } }

class Ledger(ARMObject):
    __spec__ = { 'object': 'transaction_ledger' }

class PaymentMethod(ARMObject):
    __spec__ = { 'object': 'payment_method' }

class Card(PaymentMethod):
    __spec__ = { 'polymorphic': { 'type': 'card' } }
    field_map = set(['card_number', 'expiry', 'card_code'])

class BankAccount(PaymentMethod):
    __spec__ = { 'polymorphic': { 'type': 'bank_account' } }
    field_map = set(['account_number', 'routing_number', 'account_type'])

class BillingSchedule(ARMObject):
    __spec__ = { 'object': 'billing_schedule' }

class BillingCharge(ARMObject):
    __spec__ = { 'object': 'billing_charge' }

class Invoice(ARMObject):
    __spec__ = { 'object': 'invoice' }

class LineItem(ARMObject):
    __spec__ = { 'object': 'line_item' }

class ChargeItem(LineItem):
    __spec__ = { 'polymorphic': { 'entry_type': 'charge' } }

class PaymentItem(LineItem):
    __spec__ = { 'polymorphic': { 'entry_type': 'payment' } }

class Webhook(ARMObject):
    __spec__ = { 'object': 'webhook' }

class PaymentLink(ARMObject):
    __spec__ = { 'object': 'payment_link' }

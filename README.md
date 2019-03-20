# Payload Python Library

A Python library for integrating [Payload](https://payload.co).

## Installation

## Install using pip

```bash
pip install payload-api
```

## Get Started

Once you've installed the Payload Python library to your environment,
import the `payload` module to get started. **Note:** We recommend
using the shorthand name of `pl` when importing.

```python
import payload as pl
```

### API Authentication

To authenticate with the Payload API, you'll need a live or test API key. API
keys are accessible from within the Payload dashboard.

```python
import payload as pl
pl.api_key = 'secret_key_3bW9JMZtPVDOfFNzwRdfE'
```

### Creating an Object

Interfacing with the Payload API is done primarily through Payload Objects. Below is an example of
creating a customer using the `pl.Customer` object.


```python
# Create a Customer
customer = pl.Customer.create(
	email='matt.perez@example.com',
	full_name='Matt Perez'
)
```


```python
# Create a Payment
payment = pl.Payment.create(
    amount=100.0,
    payment_method=pl.Card(
        card_number='4242 4242 4242 4242'
    )
)
```

### Accessing Object Attributes

Object attributes are accessible through both dot notation.

```python
customer.name
```

### Updating an Object

Updating an object is a simple call to the `update` object method.

```python
# Updating a customer's email
customer.update( email='matt.perez@newwork.com' )
```

### Selecting Objects

Objects can be selected using any of their attributes.

```python
# Select a customer by email
var customers = pl.Customer.filter_by(
    email='matt.perez@example.com'
)
```

Use the `pl.attr` attribute helper
interface to write powerful queries with a little extra syntax sugar.

```python
payments = pl.Payments.filter_by(
    pl.attr.amount > 100,
    pl.attr.amount < 200,
    pl.attr.description.contains("Test"),
    pl.attr.created_at > datetime(2019,2,1))
).all()
```

## Documentation

To get further information on Payload's Python library and API capabilities,
visit the unabridged [Payload Documentation](https://docs.payload.co/?python).

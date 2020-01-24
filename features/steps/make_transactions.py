import os
import time

import requests
from behave import given, when, then

CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://localhost')
ACCOUNT_SERVICE_URL = os.getenv('ACCOUNT_SERVICE_URL', 'http://localhost')
CASHIER_SERVICE_URL = os.getenv('CASHIER_SERVICE_URL', 'http://localhost')
BALANCE_SERVICE_URL = os.getenv('BALANCE_SERVICE_URL', 'http://localhost')
TRANSACTION_SERVICE_URL = os.getenv('TRANSACTION_SERVICE_URL', 'http://localhost')


@given('there is a customer "{name}"')
def create_customer(context, name):
    (first_name, surname) = name.split(' ', 2)
    create_customer_request = dict(firstName=first_name, surname=surname)
    print('Hello')
    print(CUSTOMER_SERVICE_URL)
    response = requests.post(f'{CUSTOMER_SERVICE_URL}/customers/', json=create_customer_request)

    assert response.status_code == 201, response.status_code
    body = response.json()
    context.customer_id = body['customerId']


@given('"{name}" has a new account')
def create_account(context, name):
    create_account_request = dict(customerId=context.customer_id)

    response = requests.post(f'{ACCOUNT_SERVICE_URL}/accounts/',
                             json=create_account_request)

    assert response.status_code == 201, f'{response.status_code} {response.text}'
    body = response.json()
    context.account_number = body['accountNumber']


@when('I deposit {amount:d} the account')
def deposit(context, amount):
    deposit_request = dict(accountNumber=context.account_number,
                           amount=amount,
                           operation='credit')

    response = requests.post(f'{CASHIER_SERVICE_URL}/cashier/create', json=deposit_request)
    time.sleep(2)
    assert response.status_code == 202, f'{response.status_code} {response.text}'


@when("I withdraw {amount:d} the account")
def withdraw(context, amount):
    deposit_request = dict(accountNumber=context.account_number,
                           amount=amount,
                           operation='debit')

    response = requests.post(f'{CASHIER_SERVICE_URL}/cashier/create', json=deposit_request)

    assert response.status_code == 202, f'{response.status_code} {response.text}'


@then('then balance of the account should be {amount:d}')
def assert_balance_increased(context, amount):
    balance = None
    retries = 5

    while balance != amount and retries > 0:
        response = requests.get(f'{BALANCE_SERVICE_URL}/balance/{context.account_number}')

        if response.status_code == 404:
            time.sleep(1)
            retries = retries - 1
            continue

        assert response.status_code == 200, \
            f'Expected 200 when checking balance, got {response.status_code}'

        body = response.json()
        balance = body['clearedBalance']
        retries = retries - 1
        time.sleep(1)

    assert balance == amount, f'{balance} != {amount}'

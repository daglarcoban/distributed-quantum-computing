import os
from getpass import getpass

from quantuminspire.credentials import get_basic_authentication, get_token_authentication, load_account
from quantuminspire.qiskit import QI

QI_EMAIL = os.getenv('QI_EMAIL')
QI_PASSWORD = os.getenv('QI_PASSWORD')
QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')

def QI_authenticate():
    token = load_account()
    if token is not None:
        QI.set_authentication(get_token_authentication(token), QI_URL)
    else:
        if QI_EMAIL is None or QI_PASSWORD is None:
            print('Enter email:')
            email = input()
            print('Enter password')
            password = getpass()
        else:
            email, password = QI_EMAIL, QI_PASSWORD
        QI.set_authentication(get_basic_authentication(email, password), QI_URL)

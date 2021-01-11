import numpy as np
import os
from getpass import getpass

from quantuminspire.credentials import load_account, get_token_authentication, get_basic_authentication

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute, BasicAer

from quantuminspire.qiskit import QI

QI_EMAIL = os.getenv('QI_EMAIL')
QI_PASSWORD = os.getenv('QI_PASSWORD')
QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')


def get_authentication():
    """ Gets the authentication for connecting to the Quantum Inspire API."""
    token = load_account()
    if token is not None:
        return get_token_authentication(token)
    else:
        if QI_EMAIL is None or QI_PASSWORD is None:
            print('Enter email:')
            email = input()
            print('Enter password')
            password = getpass()
        else:
            email, password = QI_EMAIL, QI_PASSWORD
        return get_basic_authentication(email, password)


def toffoli(circuit_in=QuantumCircuit, control_1=int, control_2=int, q_in=int, q_reg=QuantumRegister):
    circuit_in.h(q_reg[q_in])
    circuit_in.cx(q_reg[control_2], q_reg[q_in])
    circuit_in.tdg(q_reg[q_in])
    circuit_in.cx(q_reg[control_1], q_reg[q_in])
    circuit_in.t(q_reg[q_in])
    circuit_in.cx(q_reg[control_2], q_reg[q_in])
    circuit_in.tdg(q_reg[q_in])
    circuit_in.cx(q_reg[control_1], q_reg[q_in])
    circuit_in.t(q_reg[control_2])
    circuit_in.t(q_reg[q_in])
    circuit_in.cx(q_reg[control_1], q_reg[control_2])
    circuit_in.h(q_reg[q_in])
    circuit_in.t(q_reg[control_1])
    circuit_in.tdg(q_reg[control_2])
    circuit_in.cx(q_reg[control_1], q_reg[control_2])

    return circuit_in


if __name__ == '__main__':
    authentication = get_authentication()
    QI.set_authentication(authentication, QI_URL)
    qi_backend = QI.get_backend('QX single-node simulator')
    N = 9
    c = ClassicalRegister(N)
    q = QuantumRegister(N)
    circuit = QuantumCircuit(q, c)

    alpha = 0
    beta = 1
    circuit.initialize([alpha, beta], q[0])
    #circuit + toffoli(circuit, 6, 7, 8, q)  Toffoli Test

    print(circuit.draw())

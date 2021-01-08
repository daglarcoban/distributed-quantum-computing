import os
import numpy as np
from getpass import getpass
from math import sqrt


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


if __name__ == '__main__':

    authentication = get_authentication()
    QI.set_authentication(authentication, QI_URL)
    qi_backend = QI.get_backend('QX single-node simulator')

    q = QuantumRegister(4)
    c = ClassicalRegister(4)
    circuit = QuantumCircuit(q, c)

    alpha = 0#/sqrt(2)
    beta = 1#/sqrt(2)
    circuit.initialize([alpha, beta], q[0])

    circuit.h(q[1])
    circuit.cnot(q[1],q[2])
    circuit.barrier()
    circuit.cnot(q[0],q[1])
    circuit.barrier()
    circuit.measure(q[1],c[0])
    circuit.x(1).c_if(c,2)   #xxxxx
    circuit.x(2).c_if(c,2)
    circuit.barrier()
    circuit.h(0)
    circuit.measure(q[0],c[1])
    circuit.x(0).c_if(c,1)
    circuit.barrier()
    circuit.z(2).c_if(c,1)
    circuit.barrier()
    circuit.x(0).c_if(c,3)
    circuit.barrier()
    circuit.z(2).c_if(c,3)
    circuit.barrier()
    circuit.swap(q[2],q[3])



    circuit.draw()
    print(circuit)
    print("\nResult from the local Qiskit simulator backend:\n")
    backend = BasicAer.get_backend("qasm_simulator")
    job = execute(circuit, backend=backend, shots=1024)
    result = job.result()
    print(result.get_counts(circuit))


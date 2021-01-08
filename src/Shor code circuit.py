# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 15:45:44 2021

@author: Cynrîk
"""
import numpy as np
import os
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
    N=9
    c=ClassicalRegister(N)
    q=QuantumRegister(N)
    circ=QuantumCircuit(q,c)
    
    
    alpha = 1/np.sqrt(2)
    beta = 1/np.sqrt(2)
    circ.initialize([alpha, beta], q[0])
    
    circ.cx(q[0],q[3])
    circ.cx(q[0],q[6])
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0],q[1])
    circ.cx(q[3],q[4])
    circ.cx(q[6],q[7])
    circ.cx(q[0],q[2])
    circ.cx(q[3],q[5])
    circ.cx(q[6],q[8])
    
    # RNG=np.random.random(N)
    # for i in range(N):
    #     if RNG[i]>=0.66:
    #         circ.z(q[i])
    #         continue
    #     elif RNG[i]>=0.33 and RNG[i]<0.66:
    #         circ.x(q[i])
    #         continue
    #     else:
    #         circ.y(q[i])
    
    
    circ.cx(q[0],q[1])
    circ.cx(q[3],q[4])
    circ.cx(q[6],q[7])
    circ.cx(q[0],q[2])
    circ.cx(q[3],q[5])
    circ.cx(q[6],q[8])
    circ.ccx(q[1],q[2],q[0])
    circ.ccx(q[4],q[5],q[3])
    circ.ccx(q[7],q[8],q[6])
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0],q[3])
    circ.cx(q[0],q[6])
    circ.ccx(q[3],q[6],q[0])
    circ.measure(q,c)
    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    # Print the full state counts histogram
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]
    circ.draw()
    print(circ)
    print("\nResult from the local Qiskit simulator backend:\n")
    backend = BasicAer.get_backend("qasm_simulator")
    job = execute(circ, backend=backend, shots=1024)
    result = job.result()
    print(result.get_counts(circ))

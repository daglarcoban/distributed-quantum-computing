# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 10:48:45 2021

@author: Cynrîk
"""
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

    def get_cat_entangler(number_of_entangled_qubits):
        q = QuantumRegister(number_of_entangled_qubits + 1)
        circuit = QuantumCircuit(q)
        c = [ClassicalRegister(1) for _ in range(number_of_entangled_qubits + 1)]
        for reg in c:
            circuit.add_register(reg)
    
        #Entangle last number_of_entangled_qubits qubits
        circuit.h(q[1])
        for i in range(1, number_of_entangled_qubits):
            circuit.cx(q[i], q[i+1])
        circuit.barrier()
    
        circuit.cx(q[0], q[1])
        circuit.barrier()
    
        #Measure 2nd qubit
        circuit.measure(q[1], c[1])
        circuit.barrier()
    
        #Apply X gate on last number_of_entangled_qubits qubits
        # depending on measurement result of qubit 2
        for i in range(1, number_of_entangled_qubits + 1):
            circuit.x(q[i]).c_if(c[1], 1)
    
        return circuit
    
    def get_cat_disentangler(number_of_entangled_qubits):
        q = QuantumRegister(number_of_entangled_qubits + 1)
        circuit = QuantumCircuit(q)
        c = [ClassicalRegister(1) for _ in range(number_of_entangled_qubits + 1)]
        for reg in c:
            circuit.add_register(reg)
    
        # Apply Hadamard gate on each of the last number_of_entangled_qubits - 1 qubits
        for i in range(2, number_of_entangled_qubits + 1):
            circuit.h(q[i])
    
        # Measure each of the last number_of_entangled_qubits - 1 qubits
        # Apply X gate on each depending on corresponding measurement outcome
        for i in range(2, number_of_entangled_qubits + 1):
            circuit.measure(q[i], c[i])
            circuit.x(q[i]).c_if(c[i], 1)
    
        # Apply Z gate on first qubit depending on XOR of all measurement outcomes
        for i in range(2, number_of_entangled_qubits + 1):
            circuit.z(q[0]).c_if(c[i], 1)
    
        return circuit
    
    #c=ClassicalRegister(15)
    q=QuantumRegister(15)
    circ=QuantumCircuit(q)
    c = [ClassicalRegister(1) for _ in range(15)]
    for reg in c:
        circ.add_register(reg)
    
    
    alpha = 0
    beta = 1
    circ.initialize([alpha, beta], q[0])
    
    #CNOT from 1-4
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    
    #CNOT from 1-7
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])
    circ.cx(q[11],q[10])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])
    
    #Local section
    circ.h(q[0])
    circ.h(q[5])
    circ.h(q[10])
    circ.cx(q[0],q[2])
    circ.cx(q[5],q[7])
    circ.cx(q[10],q[12])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    circ.cx(q[4],q[3])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    circ.cx(q[9],q[8])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    circ.cx(q[14],q[13])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    
    #
    random_bit = np.random.choice([0,2,3,5,7,8,10,12,13])
    RNG=np.random.random(1)
    if RNG>=0.66:
        circ.z(q[random_bit])
    elif RNG>=0.33 and RNG<0.66:
        circ.x(q[random_bit])
    else:
        circ.y(q[random_bit])
    
    #
    circ.cx(q[0],q[2])
    circ.cx(q[5],q[7])
    circ.cx(q[10],q[12])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    circ.cx(q[4],q[3])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    circ.cx(q[9],q[8])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    circ.cx(q[14],q[13])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    
    #
    circ.h(q[0])
    circ.h(q[5])
    circ.h(q[10])
    
    circ.cx(q[2],q[0])
    circ.cx(q[7],q[5])
    circ.cx(q[12],q[10])
    
    circ.tdg(q[0])
    circ.tdg(q[5])
    circ.tdg(q[10])
    
    circ=circ.compose(get_cat_entangler(2), [q[3], q[4], q[1]], [c[3][0], c[4][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[3], q[4], q[1]], [c[3][0], c[4][0], c[1][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[8], q[9], q[6]], [c[8][0], c[9][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[8], q[9], q[6]], [c[8][0], c[9][0], c[6][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[13], q[14], q[11]], [c[13][0], c[14][0], c[11][0]])
    circ.cx(q[11],q[10])
    circ = circ.compose(get_cat_disentangler(2), [q[13], q[14], q[11]], [c[13][0], c[14][0], c[11][0]])
    
    circ.t(q[0])
    circ.t(q[2])
    circ.t(q[5])
    circ.t(q[7])
    circ.t(q[10])
    circ.t(q[12])
    
    circ.h(q[0])
    circ.cx(q[3],q[2])
    circ.h(q[5])
    circ.cx(q[8],q[7])
    circ.h(q[10])
    circ.cx(q[13],q[12])
    
    circ.tdg(q[2])
    circ.t(q[3])
    circ.tdg(q[7])
    circ.t(q[8])
    circ.tdg(q[12])
    circ.t(q[13])
    
    circ.cx(q[3],q[2])
    circ.cx(q[8],q[7])
    circ.cx(q[13],q[12])
    
    #
    circ.h(q[0])
    circ.h(q[5])
    circ.h(q[10])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])
    circ.cx(q[11],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])
    
    #
    circ.h(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    
    circ.tdg(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    
    circ.t(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    
    circ.tdg(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    
    circ.t(q[0])
    circ.t(q[5])
    
    circ.h(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])
    
    circ.tdg(q[5])
    circ.t(q[10])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])
    
    
    for i in range(15):
        circ.measure(circ.qregs[0][i], circ.cregs[i])
    qi_job = execute(circ, backend=qi_backend, shots=20)
    qi_result = qi_job.result()
    # Print the full state counts histogram
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]
    circ.draw()
    print("\nResult from the local Qiskit simulator backend:\n")
    backend = BasicAer.get_backend("qasm_simulator")
    job = execute(circ, backend=backend, shots=11)
    result = job.result()
    print(result.get_counts(circ))










































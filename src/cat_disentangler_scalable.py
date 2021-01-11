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

def get_cat_disentangler():
    q = QuantumRegister(6)
    c0 = ClassicalRegister(1)
    c1 = ClassicalRegister(1)
    c2 = ClassicalRegister(1)
    c3 = ClassicalRegister(1)
    c4 = ClassicalRegister(1)
    c5 = ClassicalRegister(1)
    c = [c0, c1, c2, c3, c4, c5]
    circuit = QuantumCircuit(q, c0, c1, c2, c3, c4, c5)

    circuit.barrier()

    # H for all entangled 1-4
    # circuit.h(q[1])
    circuit.h(q[2])
    circuit.h(q[3])
    circuit.h(q[4])

    # measure all 1-4
    # circuit.measure(q[1], c[1])
    circuit.measure(q[2], c2)
    circuit.measure(q[3], c3)
    circuit.measure(q[4], c4)

    # Mod 2 plus for 1- 4

    for i in range(3, 6):
        circuit.x(q[5]).c_if(c[i], 1)

    # Do Z if odd
    circuit.measure(q[5], c5)

    circuit.z(q[0]).c_if(c5, 1)

    for i in range(2, 5):
        circuit.x(q[i]).c_if(c[i], 1)

    print(circuit.draw())
    for i in range(5):
        circuit.measure(q[i], c[i])

    return circuit

if __name__ == '__main__':
    authentication = get_authentication()
    QI.set_authentication(authentication, QI_URL)
    qi_backend = QI.get_backend('QX single-node simulator')


    alpha = 1 / sqrt(2)
    beta = 1 / sqrt(2)
    circuit.initialize([alpha, beta], q[0])
    initialstate = [1,0]
    circuit.initialize(initialstate, q[5])


    print("\nResult from the remote Quantum Inspire backend:\n")
    qi_job = execute(circuit, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    # Print the full state counts histogram
    histogram = qi_result.get_counts(circuit)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]
    # # Print the full state probabilities histogram
    # probabilities_histogram = qi_result.get_probabilities(circuit)
    # print('\nState\tProbabilities')
    # [print('{0}\t\t{1}'.format(state, val)) for state, val in probabilities_histogram.items()]

    print("\nResult from the local Qiskit simulator backend:\n") # Update!
    backend = BasicAer.get_backend("qasm_simulator")
    job = execute(circuit, backend=backend, shots=1024)
    result = job.result()
    print(result.get_counts(circuit))

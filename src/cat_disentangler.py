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

    q = QuantumRegister(6)
    c = ClassicalRegister(6)
    circuit = QuantumCircuit(q, c)

    alpha = 1 / sqrt(2)
    beta = 1 / sqrt(2)
    circuit.initialize([alpha, beta], q[0])
    initialstate = [1,0]
    circuit.initialize(initialstate, q[5])

    # Entangle qubit 2-5 (index 1-4)
    circuit.h(q[1])
    circuit.cx(q[1], q[2])
    circuit.cx(q[2], q[3])
    circuit.cx(q[3], q[4])

    circuit.barrier()
    circuit.cx(q[0], q[1])
    circuit.measure(q[1], c[1])
    circuit.barrier()

    # Use classical measurement result of qubit 2 to control x gates
    # The value in the c_if is 2 because it will be interpreted in binary: 00010
    # Exactly what we want: we want apply the x if the 2nd bit is 1
    # The other values in the register will be 0 since they are not measured yet

    circuit.x(q[1]).c_if(c, 2)
    circuit.x(q[2]).c_if(c, 2)
    circuit.x(q[3]).c_if(c, 2)
    circuit.x(q[4]).c_if(c, 2)

    print(circuit.draw())

    # DISENTANGLER

    circuit.barrier()

    # H for all entangled 1-4
    # circuit.h(q[1])
    circuit.h(q[2])
    circuit.h(q[3])
    circuit.h(q[4])

    # measure all 1-4
    # circuit.measure(q[1], c[1])
    circuit.measure(q[2], c[2])
    circuit.measure(q[3], c[3])
    circuit.measure(q[4], c[4])

    # Mod 2 plus for 1- 4

    # for i in range(1, 16, 2):
    #     circuit.x(q[5]).c_if(c, i) # 1, 3, 5, 7, 9, 11, 13, 15 # FIRST LINE
    #

    for i in range(2, 16, 4):
        circuit.x(q[5]).c_if(c, i)  # 2, 6, 10, 14 # SECOND LINE

    for i in range(3, 16, 4):
        circuit.x(q[5]).c_if(c, i)  # 3, 7, 11, 15

    for i in range(4, 8):
        circuit.x(q[5]).c_if(c, i) # 4, 5, 6, 7

    for i in range(12, 16):
        circuit.x(q[5]).c_if(c, i) # 12, 13, 14, 15

    for i in range(8, 16):
        circuit.x(q[5]).c_if(c, i) # 8, 9, 10, 11, 12, 13, 14, 15

    # Do Z if odd
    circuit.measure(q[5], c[5])

    for i in range(8, 16):
         circuit.z(q[0]).c_if(c, i) # 8, 9, 10, 11, 12, 13, 14, 15


    i = 4
    j = 0
    while i < 64:
        if j < 4:
            circuit.x(q[2]).c_if(c, i)
            j += 1
            i += 1
        else:
            j = 0
            i += 4

    i = 8
    j = 0
    while i < 64:
        if j < 8:
            circuit.x(q[3]).c_if(c, i)
            j += 1
            i += 1
        else:
            j = 0
            i += 8

    i = 16
    j = 0
    while i < 64:
        if j < 16:
            circuit.x(q[4]).c_if(c, i)
            j += 1
            i += 1
        else:
            j = 0
            i += 16

    print(circuit.draw())
    circuit.measure(q, c)

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

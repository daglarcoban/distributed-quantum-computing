import os
from math import sqrt

from qiskit import execute, BasicAer, QuantumRegister, ClassicalRegister, QuantumCircuit
from quantuminspire.qiskit import QI

from src.cat_disentangler import get_cat_disentangler
from src.cat_entangler import get_cat_entangler
from src.setup import get_authentication

QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')

if __name__ == '__main__':
    authentication = get_authentication()
    QI.set_authentication(authentication, QI_URL)

    q = QuantumRegister(4)
    circuit = QuantumCircuit(q)
    c = [ClassicalRegister(1), ClassicalRegister(1), ClassicalRegister(1), ClassicalRegister(1)]
    for reg in c:
        circuit.add_register(reg)

    alpha = sqrt(50)/sqrt(100)
    beta = sqrt(50)/sqrt(100)
    circuit.initialize([alpha, beta], q[0])

    circuit = circuit.compose(get_cat_entangler(2), [0, 1, 2])
    circuit.cx(q[2], q[3])
    circuit = circuit.compose(get_cat_disentangler(2), [0, 1, 2])
    for i in range(4):
        circuit.measure(circuit.qregs[0][i], circuit.cregs[i])
    print(circuit.draw())

    print("\nResult from the remote Quantum Inspire backend:\n")
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circuit, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circuit)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]
    # probabilities_histogram = qi_result.get_probabilities(circuit)
    # print('\nState\tProbabilities')
    # [print('{0}\t\t{1}'.format(state, val)) for state, val in probabilities_histogram.items()]

    # print("\nResult from the local Qiskit simulator backend:\n")
    # backend = BasicAer.get_backend("qasm_simulator")
    # job = execute(circuit, backend=backend, shots=1024)
    # result = job.result()
    # print(result.get_counts(circuit))
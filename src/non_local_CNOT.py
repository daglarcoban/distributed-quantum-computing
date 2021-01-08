import os

from qiskit import execute, circuit, BasicAer, QuantumRegister, ClassicalRegister, QuantumCircuit
from quantuminspire.qiskit import QI

from src.cat_entangler import get_cat_entangler
from src.setup import get_authentication

QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')

if __name__ == '__main__':
    authentication = get_authentication()
    QI.set_authentication(authentication, QI_URL)

    q = QuantumRegister(2)
    c = ClassicalRegister(2)
    circuit = QuantumCircuit(q, c)
    circuit.cx()

    get_cat_entangler(2) + circuit + get_cat_disentangler(2)

    print("\nResult from the remote Quantum Inspire backend:\n")
    qi_backend = QI.get_backend('QX single-node simulator')
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

    print("\nResult from the local Qiskit simulator backend:\n")
    backend = BasicAer.get_backend("qasm_simulator")
    job = execute(circuit, backend=backend, shots=1024)
    result = job.result()
    print(result.get_counts(circuit))

    #Note the bits in the result are reversed to what we are used to, so:
    # the first bit is written down at the right, the 2nd bit left to it... the 5th bit on the far left
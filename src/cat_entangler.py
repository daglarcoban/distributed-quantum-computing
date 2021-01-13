import os
from math import sqrt

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute, BasicAer
from quantuminspire.qiskit import QI

from src.setup import get_authentication

QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')

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

#Test cat-entangler
if __name__ == '__main__':
    authentication = get_authentication()
    QI.set_authentication()

    number_of_entangled_qubits = 4
    q = QuantumRegister(number_of_entangled_qubits + 1)
    circuit = QuantumCircuit(q)
    c = [ClassicalRegister(1) for _ in range(number_of_entangled_qubits + 1)]
    for reg in c:
        circuit.add_register(reg)

    alpha = sqrt(50)/sqrt(100)
    beta = sqrt(50)/sqrt(100)
    circuit.initialize([alpha, beta], q[0])

    circuit = circuit.compose(get_cat_entangler(number_of_entangled_qubits), range(number_of_entangled_qubits + 1))
    for i in range(number_of_entangled_qubits + 1):
        circuit.measure(circuit.qregs[0][i], circuit.cregs[i])
    print(circuit.draw())

    # The result is either 00000 or 11101
    # This is correct, since the order of the bits is reversed compared to what we are used to when we write it down

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

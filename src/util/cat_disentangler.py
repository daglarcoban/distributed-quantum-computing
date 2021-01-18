from math import sqrt

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute

from quantuminspire.qiskit import QI

from src.util.cat_entangler import get_cat_entangler_circuit
from src.util.authentication import QI_authenticate

def get_cat_disentangler_circuit(number_of_entangled_qubits):
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

#Test cat-disentangler (preceded by cat-entangler for correct input)
if __name__ == '__main__':
    number_of_entangled_qubits = 4
    q = QuantumRegister(number_of_entangled_qubits + 1)
    circuit = QuantumCircuit(q)
    c = [ClassicalRegister(1) for _ in range(number_of_entangled_qubits + 1)]
    for reg in c:
        circuit.add_register(reg)

    alpha = sqrt(50) / sqrt(100)
    beta = sqrt(50) / sqrt(100)
    circuit.initialize([alpha, beta], q[0])

    circuit = circuit.compose(get_cat_entangler_circuit(number_of_entangled_qubits), range(number_of_entangled_qubits + 1))
    circuit = circuit.compose(get_cat_disentangler_circuit(number_of_entangled_qubits), range(number_of_entangled_qubits + 1))

    print(circuit.draw())

    for i in range(number_of_entangled_qubits + 1):
        circuit.measure(circuit.qregs[0][i], circuit.cregs[i])

    # The result is either 00000 or 00001
    # This is correct, since the order of the bits is reversed compared to what we are used to when we write it down

    print("\nResult from the remote Quantum Inspire backend:\n")
    QI_authenticate()
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

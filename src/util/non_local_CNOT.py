from math import sqrt

from qiskit import execute, QuantumRegister, ClassicalRegister, QuantumCircuit
from quantuminspire.qiskit import QI

from src.util.cat_disentangler import get_cat_disentangler_circuit
from src.util.cat_entangler import get_cat_entangler_circuit
from src.util.authentication import QI_authenticate

#Test/example of how to implement a (ciruit with a) non-local CNOT
if __name__ == '__main__':
    q = QuantumRegister(4)
    circuit = QuantumCircuit(q)
    c = [ClassicalRegister(1), ClassicalRegister(1), ClassicalRegister(1), ClassicalRegister(1)]
    for reg in c:
        circuit.add_register(reg)

    alpha = sqrt(50)/sqrt(100)
    beta = sqrt(50)/sqrt(100)
    circuit.initialize([alpha, beta], q[0])

    circuit = circuit.compose(get_cat_entangler_circuit(2), [0, 1, 2])
    circuit.cx(q[2], q[3])
    circuit = circuit.compose(get_cat_disentangler_circuit(2), [0, 1, 2])

    for i in range(4):
        circuit.measure(circuit.qregs[0][i], circuit.cregs[i])
    print(circuit.draw())

    print("\nResult from the remote Quantum Inspire backend:\n")
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circuit, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circuit)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

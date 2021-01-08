import os
from math import sqrt

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute, BasicAer
from quantuminspire.qiskit import QI

from src.setup import get_authentication

QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')

#TODO: MAKE NUMBER OF QUBITS TO BE ENTANGLED VARIABLE
def get_cat_entangler():
    q = QuantumRegister(5)
    c = ClassicalRegister(5)
    circuit = QuantumCircuit(q, c)

    alpha = 1/sqrt(2)
    beta = 1/sqrt(2)
    circuit.initialize([alpha, beta], q[0])

    #Entangle qubit 2-5 (index 1-4)
    circuit.h(q[1])
    circuit.cx(q[1], q[2])
    circuit.cx(q[2], q[3])
    circuit.cx(q[3], q[4])
    circuit.barrier()

    #Measure 2nd qubit
    circuit.cx(q[0], q[1])
    circuit.measure(q[1], c[1])
    circuit.barrier()

    #Use classical measurement result of qubit 2 to control x gates
    #The value in the c_if is 2 because it will be interpreted in binary: 00010
    #Exactly what we want: we want apply the x if the 2nd bit is 1
    #The other values in the register will be 0 since they are not measured yet
    circuit.x(q[1]).c_if(c, 2)
    circuit.x(q[2]).c_if(c, 2)
    circuit.x(q[3]).c_if(c, 2)
    circuit.x(q[4]).c_if(c, 2)

    return circuit

if __name__ == '__main__':
    authentication = get_authentication()
    QI.set_authentication()

    circuit = get_cat_entangler()
    circuit.measure(circuit.qregs[0], circuit.cregs[0])
    print(circuit.draw())

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

    #The result is either 00000 or 11101. This is correct, since the order of bits is reversed compared
    #to what we are used to when we write it down
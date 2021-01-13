from numpy import pi

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute, BasicAer

#FUNCTIONS FROM THE QISKIT WEBSITE

def qft_rotations(circuit, n):
    if n == 0: # Exit function if circuit is empty
        return circuit
    n -= 1 # Indexes start from 0
    circuit.h(n) # Apply the H-gate to the most significant qubit
    for qubit in range(n):
        # For each less significant qubit, we need to do a
        # smaller-angled controlled rotation:
        circuit.cu1(pi/2**(n-qubit), qubit, n)

def swap_registers(circuit, n):
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft(circuit, n):
    """QFT on the first n qubits in circuit"""
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit

if __name__ == '__main__':
    q = QuantumRegister(5)
    c = ClassicalRegister(5)
    qc = QuantumCircuit(q,c)
    qft(qc, 5)
    qc.measure(q,c)
    backend = BasicAer.get_backend("qasm_simulator")
    job = execute(qc, backend=backend, shots=1024)
    result = job.result()
    print(result.get_counts(qc))
    print(qc.draw())

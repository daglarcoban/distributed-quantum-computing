import numpy as np
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute
from quantuminspire.qiskit import QI
from src.util.authentication import QI_authenticate
from src.util.cat_disentangler import get_cat_disentangler_circuit
from src.util.cat_entangler import get_cat_entangler_circuit

def get_shor_code_lnn_combined(error_type = None, error_bit = None, a = None, b = None):
    q = QuantumRegister(12)
    circ = QuantumCircuit(q)
    c = [ClassicalRegister(1) for _ in range(12)]
    for reg in c:
        circ.add_register(reg)

    #Initialize the main qubit
    alpha = 0  # 1 / sqrt(2)
    if a is not None:
        alpha = a
    beta = 1  # / sqrt(2)
    if b is not None:
        beta = b
    circ.initialize([alpha, beta], q[0])


    # First part of the phase flip code
    circ = circ.compose(get_cat_entangler_circuit(2), [q[0], q[1], q[5]], [c[0][0], c[1][0], c[5][0]])
    circ.cx(q[5], q[4])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[0], q[1], q[5]], [c[0][0], c[1][0], c[5][0]])

    # CNOT from 1-7
    circ = circ.compose(get_cat_entangler_circuit(2), [q[0], q[1], q[9]], [c[0][0], c[1][0], c[9][0]])
    circ.cx(q[9], q[8])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[0], q[1], q[9]], [c[0][0], c[1][0], c[9][0]])

    # hadamard gate section 1
    circ.h(q[0])
    circ.h(q[4])
    circ.h(q[8])
    circ.barrier()

    # First part of the bit flip code
    circ.cx(q[0], q[2])
    circ.cx(q[4], q[6])
    circ.cx(q[8], q[10])

    circ.swap(q[0], q[2])
    circ.swap(q[4], q[6])
    circ.swap(q[8], q[10])

    circ.cx(q[2], q[3])
    circ.cx(q[6], q[7])
    circ.cx(q[10], q[11])

    circ.swap(q[0], q[2])
    circ.swap(q[4], q[6])
    circ.swap(q[8], q[10])

    # Quantum error channel which generates a bit or phase flip error or both in one of the qubits
    if error_type == 'random':
        RNG = np.random.random(1)
        if RNG >= 0.66:
            error_type = 'z'
        elif RNG >= 0.33 and RNG < 0.66:
            error_type = 'x'
        else:
            error_type = 'y'
    if error_bit == 'random':
        error_bit = np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])

    if error_bit != None:
        if error_type == 'z':
            circ.z(q[error_bit])
        elif error_type == 'x':
            circ.x(q[error_bit])
        elif error_type == 'y':
            circ.y(q[error_bit])
    circ.barrier()

    # Second part of the bit flip code
    circ.cx(q[0], q[2])
    circ.cx(q[4], q[6])
    circ.cx(q[8], q[10])

    circ.swap(q[0], q[2])
    circ.swap(q[4], q[6])
    circ.swap(q[8], q[10])

    circ.cx(q[2], q[3])
    circ.cx(q[6], q[7])
    circ.cx(q[10], q[11])

    circ.swap(q[0], q[2])
    circ.swap(q[4], q[6])
    circ.swap(q[8], q[10])

    # hadamard gate section 2
    circ.h(q[0])
    circ.h(q[4])
    circ.h(q[8])
    circ.barrier()

    circ.cx(q[2], q[0])
    circ.cx(q[6], q[4])
    circ.cx(q[10], q[8])

    circ.tdg(q[0])
    circ.tdg(q[4])
    circ.tdg(q[8])

    circ.swap(q[2], q[0])
    circ.swap(q[6], q[4])
    circ.swap(q[10], q[8])

    circ.cx(q[3], q[2])
    circ.cx(q[7], q[6])
    circ.cx(q[11], q[10])

    circ.swap(q[2], q[0])
    circ.swap(q[6], q[4])
    circ.swap(q[10], q[8])

    circ.t(q[0])
    circ.t(q[4])
    circ.t(q[8])

    circ.cx(q[2], q[0])
    circ.cx(q[6], q[4])
    circ.cx(q[10], q[8])

    circ.tdg(q[0])
    circ.tdg(q[4])
    circ.tdg(q[8])

    circ.swap(q[2], q[0])
    circ.swap(q[6], q[4])
    circ.swap(q[10], q[8])

    circ.cx(q[3], q[2])
    circ.cx(q[7], q[6])
    circ.cx(q[11], q[10])

    circ.swap(q[2], q[0])
    circ.swap(q[6], q[4])
    circ.swap(q[10], q[8])

    circ.t(q[0])
    circ.t(q[2])
    circ.t(q[4])
    circ.t(q[6])
    circ.t(q[8])
    circ.t(q[10])

    circ.cx(q[3], q[2])
    circ.cx(q[7], q[6])
    circ.cx(q[11], q[10])

    circ.tdg(q[2])
    circ.t(q[3])
    circ.tdg(q[6])
    circ.t(q[7])
    circ.tdg(q[10])
    circ.t(q[11])

    circ.cx(q[3], q[2])
    circ.cx(q[7], q[6])
    circ.cx(q[11], q[10])

    # circ.barrier()

    # Second part of the phase flip code
    circ = circ.compose(get_cat_entangler_circuit(2), [q[0], q[1], q[5]], [c[0][0], c[1][0], c[5][0]])
    circ.cx(q[5], q[4])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[0], q[1], q[5]], [c[0][0], c[1][0], c[5][0]])

    circ = circ.compose(get_cat_entangler_circuit(2), [q[0], q[1], q[9]], [c[0][0], c[1][0], c[9][0]])
    circ.cx(q[9], q[8])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[0], q[1], q[9]], [c[0][0], c[1][0], c[9][0]])

    # Final Toffoli gate
    circ.h(q[0])

    circ = circ.compose(get_cat_entangler_circuit(2), [q[4], q[5], q[1]], [c[4][0], c[5][0], c[1][0]])
    circ.cx(q[1], q[0])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[4], q[5], q[1]], [c[4][0], c[5][0], c[1][0]])

    circ.tdg(q[0])

    circ = circ.compose(get_cat_entangler_circuit(2), [q[8], q[9], q[1]], [c[8][0], c[9][0], c[1][0]])
    circ.cx(q[1], q[0])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[8], q[9], q[1]], [c[8][0], c[9][0], c[1][0]])

    circ.t(q[0])

    circ = circ.compose(get_cat_entangler_circuit(2), [q[4], q[5], q[1]], [c[4][0], c[5][0], c[1][0]])
    circ.cx(q[1], q[0])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[4], q[5], q[1]], [c[4][0], c[5][0], c[1][0]])

    circ.tdg(q[0])

    circ = circ.compose(get_cat_entangler_circuit(2), [q[8], q[9], q[1]], [c[8][0], c[9][0], c[1][0]])
    circ.cx(q[1], q[0])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[8], q[9], q[1]], [c[8][0], c[9][0], c[1][0]])

    circ.t(q[0])
    circ.t(q[4])

    circ.h(q[0])

    circ = circ.compose(get_cat_entangler_circuit(2), [q[8], q[9], q[5]], [c[8][0], c[9][0], c[5][0]])
    circ.cx(q[5], q[4])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[8], q[9], q[5]], [c[8][0], c[9][0], c[5][0]])

    circ.tdg(q[4])
    circ.t(q[8])

    circ = circ.compose(get_cat_entangler_circuit(2), [q[8], q[9], q[5]], [c[8][0], c[9][0], c[5][0]])
    circ.cx(q[5], q[4])
    circ = circ.compose(get_cat_disentangler_circuit(2), [q[8], q[9], q[5]], [c[8][0], c[9][0], c[5][0]])

    return circ

if __name__ == '__main__':
    a = 0 #1 / np.sqrt(2)
    b = 1 #/ np.sqrt(2)

    circ = get_shor_code_lnn_combined('random', 'random', a, b)
    print(circ.draw())
    print("Circuit depth: ", circ.depth()) #measure at the end + error block (which might introduce extra gate) should be commented out

    #measure all so we can see results
    for i in range(12):
        circ.measure(circ.qregs[0][i], circ.cregs[i])

    # print results
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

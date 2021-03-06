import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute

from quantuminspire.qiskit import QI

from src.util.authentication import QI_authenticate

#error_type and error_bit are None by default, so no error is introduced
#if you provide 'random' for error_type and/or error_bit, a random error type/bit will be chosen
#otherwise, for error_type you can provide: 'x' (bit flip), 'z' (phase flip) or 'y' (both)
#         , for error_bit, any index from [0, 1 ... 8] can be chosen to introduce the error on
def get_shor_code_normal_circuit(error_type = None, error_bit = None, a = None, b = None):
    c = ClassicalRegister(9)
    q = QuantumRegister(9)
    circ = QuantumCircuit(q, c)

    #Initialize the main qubit that will be error corrected
    alpha = 0  # 1 / sqrt(2)
    if a is not None:
        alpha = a
    beta = 1  # / sqrt(2)
    if b is not None:
        beta = b
    circ.initialize([alpha, beta], q[0])

    #First part of the phase flip code
    circ.cx(q[0], q[3])
    circ.cx(q[0], q[6])

    #First part of the bit flip code
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0], q[1])
    circ.cx(q[3], q[4])
    circ.cx(q[6], q[7])
    circ.cx(q[0], q[2])
    circ.cx(q[3], q[5])
    circ.cx(q[6], q[8])

    circ.barrier()

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

    #Second part of the bit flip code
    circ.cx(q[0], q[1])
    circ.cx(q[3], q[4])
    circ.cx(q[6], q[7])
    circ.cx(q[0], q[2])
    circ.cx(q[3], q[5])
    circ.cx(q[6], q[8])
    circ.ccx(q[1], q[2], q[0])
    circ.ccx(q[4], q[5], q[3])
    circ.ccx(q[7], q[8], q[6])

    #Second part of the phase flip code
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0], q[3])
    circ.cx(q[0], q[6])
    circ.ccx(q[3], q[6], q[0])

    return circ

if __name__ == '__main__':
    a = 0 #1 / sqrt(2)
    b = 1 #/ sqrt(2)

    circ = get_shor_code_normal_circuit('random', 'random', a, b)

    print(circ.draw())
    print("Circuit depth: ", circ.depth()) #measure at the end + error block (which might introduce extra gate) should be commented out

    #Measure all so we can see results
    circ.measure(circ.qregs[0], circ.cregs[0])

    #print results
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

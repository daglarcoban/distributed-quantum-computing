import warnings

import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute

from quantuminspire.qiskit import QI
from src.cccx import cccx
from src.util.authentication import QI_authenticate

def get_shor_code_extended(error_type = None, error_bit = None, a = None, b = None):
    c = ClassicalRegister(16)
    q = QuantumRegister(16)
    circ = QuantumCircuit(q, c)

    alpha = 0  # 1 / sqrt(2)
    if a is not None:
        alpha = a
    beta = 1  # / sqrt(2)
    if b is not None:
        beta = b
    circ.initialize([alpha, beta], q[0])

    circ.cx(q[0], q[4])
    circ.cx(q[0], q[8])
    circ.cx(q[0], q[12])

    circ.h(q[0])
    circ.h(q[4])
    circ.h(q[8])
    circ.h(q[12])

    circ.cx(q[0], q[1])
    circ.cx(q[0], q[2])
    circ.cx(q[0], q[3])

    circ.cx(q[4], q[5])
    circ.cx(q[4], q[6])
    circ.cx(q[4], q[7])

    circ.cx(q[8], q[9])
    circ.cx(q[8], q[10])
    circ.cx(q[8], q[11])

    circ.cx(q[12], q[13])
    circ.cx(q[12], q[14])
    circ.cx(q[12], q[15])

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
        error_bit = np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    if error_bit != None:
        if error_type == 'z':
            circ.z(q[error_bit])
        elif error_type == 'x':
            circ.x(q[error_bit])
        elif error_type == 'y':
            circ.y(q[error_bit])
    circ.barrier()

    circ.cx(q[0], q[1])
    circ.cx(q[0], q[2])
    circ.cx(q[0], q[3])

    circ.cx(q[4], q[5])
    circ.cx(q[4], q[6])
    circ.cx(q[4], q[7])

    circ.cx(q[8], q[9])
    circ.cx(q[8], q[10])
    circ.cx(q[8], q[11])

    circ.cx(q[12], q[13])
    circ.cx(q[12], q[14])
    circ.cx(q[12], q[15])
    circ.mct
    # circ.mct([q[1], q[2], q[3]], q[0])
    # circ.mct([q[5], q[6], q[7]], q[4], )
    # circ.mct([q[9], q[10], q[11]], q[8])
    # circ.mct([q[13], q[14], q[15]], q[12])
    cccx(circ, q[1], q[2], q[3], q[0])
    cccx(circ, q[5], q[6], q[7], q[4])
    cccx(circ, q[9], q[10], q[11], q[8])
    cccx(circ, q[13], q[14], q[15], q[12])

    circ.h(q[0])
    circ.h(q[4])
    circ.h(q[8])
    circ.h(q[12])

    circ.cx(q[0], q[4])
    circ.cx(q[0], q[8])
    circ.cx(q[0], q[12])

    #circ.mct([q[12], q[8], q[4]], q[0], None, mode='advanced')
    cccx(circ,q[12], q[8], q[4], q[0])
    # print(circ.draw())
    print("Circuit depth: ",
          circ.depth())  # measure at the end + error block (which might introduce extra gate) should be commented out

    # measure all so we can see results
    circ.measure(q, c)

    return circ

if __name__ == '__main__':
    print("Testing Extended shore code")
    print("-------------------------")
    warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
    for init_state in [0, 1]:
        for bit in range(16):
            for error in ['x', 'y', 'z', None]:
                alpha = (1 + init_state) % 2
                beta = init_state
                print("init state: {}, bit: {}, error: {}".format(init_state, bit, error))

                circ = get_shor_code_extended(error, bit, alpha, beta)

                QI_authenticate()
                qi_backend = QI.get_backend('QX single-node simulator')
                qi_job = execute(circ, backend=qi_backend, shots=64)
                qi_result = qi_job.result()
                histogram = qi_result.get_counts(circ)
                result_state = list(histogram.items())[0][0]

                result_first_bit = result_state[-1]
                result = result_first_bit == str(init_state)
                if (result != True):
                    print("ERROR")
                    exit(1)
                else:
                    print(result)
                    print("-------------------------")

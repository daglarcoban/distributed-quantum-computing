import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute

from quantuminspire.qiskit import QI

from src.util.authentication import QI_authenticate

if __name__ == '__main__':
    c = ClassicalRegister(16)
    q = QuantumRegister(16)
    circ = QuantumCircuit(q, c)

    alpha = 1
    beta = 0
    circ.initialize([alpha, beta], q[0])

    circ.cx(q[0], q[4])
    circ.cx(q[0], q[8])
    circ.cx(q[0],q[12])

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

    random_bit = np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    RNG = np.random.random(1)
    if RNG >= 0.66:
        circ.z(q[random_bit])
    elif RNG >= 0.33 and RNG < 0.66:
        circ.x(q[random_bit])
    else:
        circ.y(q[random_bit])

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

    circ.mct([q[1], q[2], q[3]], q[0])
    circ.mct([q[5], q[6], q[7]], q[4], )
    circ.mct([q[9], q[10], q[11]], q[8])
    circ.mct([q[13], q[14], q[15]], q[12])

    circ.h(q[0])
    circ.h(q[4])
    circ.h(q[8])
    circ.h(q[12])

    circ.cx(q[0], q[4])
    circ.cx(q[0], q[8])
    circ.cx(q[0], q[12])
    circ.mct([q[12], q[8], q[4]], q[0], None, mode='advanced')

    print(circ.draw())
    print("Circuit depth: ",
          circ.depth())  # measure at the end + error block (which might introduce extra gate) should be commented out

    # measure all so we can see results
    circ.measure(q, c)

    # print results
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

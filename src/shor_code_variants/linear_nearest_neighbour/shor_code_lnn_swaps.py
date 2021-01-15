import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute

from quantuminspire.qiskit import QI

from src.util.authentication import QI_authenticate

if __name__ == '__main__':
    c=ClassicalRegister(9)
    q=QuantumRegister(9)
    circ=QuantumCircuit(q,c)

    alpha = 1
    beta = 0#sqrt(50) / sqrt(100)
    circ.initialize([alpha, beta], q[0])

    #cnot section 1
    circ.swap(q[0],q[1])
    circ.swap(q[1], q[2])
    circ.cnot(q[2],q[3])
    circ.swap(q[2],q[3])
    circ.swap(q[3],q[4])
    circ.swap(q[2], q[3])
    circ.swap(q[4],q[5])
    circ.cnot(q[5],q[6])
    circ.swap(q[4],q[5])
    circ.swap(q[3],q[4])
    circ.swap(q[2], q[3])
    circ.swap(q[3], q[4])
    circ.swap(q[1], q[2])
    circ.swap(q[0], q[1])
    circ.barrier()

    #hadamard gate section 1
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.barrier()

    #cnot-small section 1
    for i in (0,3,6):
        circ.cnot(q[0+i],q[1+i])
        circ.swap(q[0+i],q[1+i])
        circ.cnot(q[1 + i], q[2 + i])
        circ.swap(q[0 + i], q[1 + i])
    circ.barrier()

    #error block section
    random_bit = np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
    RNG = np.random.random(1)
    if RNG >= 0.66:
        circ.z(q[random_bit])
    elif RNG >= 0.33 and RNG < 0.66:
        circ.x(q[random_bit])
    else:
        circ.y(q[random_bit])
    circ.barrier()


    #cnot-small section 2
    for i in (0,3,6):
        circ.cnot(q[0+i],q[1+i])
        circ.swap(q[0+i],q[1+i])
        circ.cnot(q[1 + i], q[2 + i])
        circ.swap(q[0 + i], q[1 + i])
    circ.barrier()

    #hadamard gate section 2
    # circ.h(q[0])
    # circ.h(q[3])
    # circ.h(q[6])
    # circ.barrier()

    #tof gate section 1
    for i in (0,3,6):
        # circ.h(q[0+i])
        circ.cnot(q[1+i],q[0+i])
        circ.tdg(q[0+i])
        circ.swap(q[0+i],q[1+i])
        circ.cnot(q[2+i],q[1+i])
        circ.swap(q[0+i], q[1+i])
        circ.t(q[0+i])
        circ.cnot(q[1+i],q[0+i])
        circ.tdg(q[0 + i])
        circ.swap(q[0+i],q[1+i])
        circ.cnot(q[2+i],q[1+i])
        circ.swap(q[0+i],q[1+i])
        circ.t(q[0+i])
        circ.t(q[1+i])
        circ.h(q[0+i])
        circ.cnot(q[2+i],q[1+i])
        circ.tdg(q[1+i])
        circ.t(q[2+i])
        circ.cnot(q[2 + i], q[1 + i])
        #circ.h(q[0+i])

    circ.barrier()

    #hadamard gate section 3
    # circ.h(q[0])
    # circ.h(q[3])
    # circ.h(q[6])
    circ.barrier()

    # cnot section 1
    circ.swap(q[0], q[1])
    circ.swap(q[1], q[2])
    circ.cnot(q[2], q[3])
    circ.swap(q[2], q[3])
    circ.swap(q[3], q[4])
    circ.swap(q[2], q[3])
    circ.swap(q[4], q[5])
    circ.cnot(q[5], q[6])
    circ.swap(q[4], q[5])
    circ.swap(q[3], q[4])
    circ.swap(q[2], q[3])
    circ.swap(q[3], q[4])
    circ.swap(q[1], q[2])
    circ.swap(q[0], q[1])
    circ.barrier()

    #tof gate final
    circ.h(q[0])
    circ.swap(q[0],q[1])
    circ.swap(q[1], q[2])
    circ.cnot(q[3],q[2])
    circ.tdg(q[2])
    circ.swap(q[2],q[3])
    circ.swap(q[3], q[4])
    circ.swap(q[4], q[5])
    circ.cnot(q[6],q[5])
    circ.t(q[5])
    circ.swap(q[4],q[5])
    circ.swap(q[3], q[4])
    circ.swap(q[3], q[2])
    circ.cnot(q[3],q[2])
    circ.tdg(q[2])
    circ.swap(q[2],q[3])
    circ.swap(q[3],q[4])
    circ.swap(q[4],q[5])
    circ.cnot(q[6],q[5])
    circ.swap(q[4],q[5])
    circ.swap(q[3], q[4])
    circ.swap(q[3], q[2])
    circ.swap(q[2],q[1])
    circ.swap(q[1],q[0])
    circ.t(q[0])
    circ.h(q[0])
    circ.barrier()
    circ.t(q[3])
    circ.swap(q[3],q[4])
    circ.swap(q[4],q[5])
    circ.cnot(q[6],q[5])
    circ.tdg(q[5])
    circ.t(q[6])
    circ.cnot(q[6], q[5])
    circ.swap(q[4], q[5])
    circ.swap(q[3], q[4])

    print(circ.draw())
    print("Circuit depth: ", circ.depth()) #measure at the end + error block (which might introduce extra gate) should be commented out

    #measure all so we can see results
    circ.measure(q, c)

    #print results
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute

from quantuminspire.qiskit import QI

from src.util.authentication import QI_authenticate

if __name__ == '__main__':
    c=ClassicalRegister(9)
    q=QuantumRegister(9)
    circ=QuantumCircuit(q,c)
    #Initialize the main qubit that will be error corrected
    alpha = 1/np.sqrt(2)
    beta = 1/np.sqrt(2)
    circ.initialize([alpha, beta], q[0])

    #First part of the phase flip code
    circ.cx(q[0],q[3])
    circ.cx(q[0],q[6])

    #First part of the bit flip code
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0],q[1])
    circ.cx(q[3],q[4])
    circ.cx(q[6],q[7])
    circ.cx(q[0],q[2])
    circ.cx(q[3],q[5])
    circ.cx(q[6],q[8])

    #Quantum error channel which generates a bit or phase flip error or both in one of the qubits
    random_bit = np.random.choice([0,1,2,3,4,5,6,7,8])
    RNG=np.random.random(1)
    if RNG>=0.66:
        circ.z(q[random_bit])
    elif RNG>=0.33 and RNG<0.66:
        circ.x(q[random_bit])
    else:
        circ.y(q[random_bit])

    #Second part of the bit flip code
    circ.cx(q[0],q[1])
    circ.cx(q[3],q[4])
    circ.cx(q[6],q[7])
    circ.cx(q[0],q[2])
    circ.cx(q[3],q[5])
    circ.cx(q[6],q[8])
    circ.ccx(q[1],q[2],q[0])
    circ.ccx(q[4],q[5],q[3])
    circ.ccx(q[7],q[8],q[6])

    #Second part of the phase flip code
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0],q[3])
    circ.cx(q[0],q[6])
    circ.ccx(q[3],q[6],q[0])

    print(circ.draw())
    print("Circuit depth: ", circ.depth())

    #Measure all so we can see results
    circ.measure(q, c)

    #print results
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

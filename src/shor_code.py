import numpy as np
import os

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute, BasicAer

from quantuminspire.qiskit import QI

from src.setup import get_authentication

QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')

if __name__ == '__main__':

    authentication = get_authentication()
    QI.set_authentication(authentication, QI_URL)
    qi_backend = QI.get_backend('QX single-node simulator')
    N=9
    c=ClassicalRegister(N)
    q=QuantumRegister(N)
    circ=QuantumCircuit(q,c)

    alpha = 0
    beta = 1
    circ.initialize([alpha, beta], q[0])
    
    circ.cx(q[0],q[3])
    circ.cx(q[0],q[6])
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0],q[1])
    circ.cx(q[3],q[4])
    circ.cx(q[6],q[7])
    circ.cx(q[0],q[2])
    circ.cx(q[3],q[5])
    circ.cx(q[6],q[8])

    random_bit = np.random.choice([0,1,2,3,4,5,6,7,8])
    RNG=np.random.random(1)
    if RNG>=0.66:
        circ.z(q[random_bit])
    elif RNG>=0.33 and RNG<0.66:
        circ.x(q[random_bit])
    else:
        circ.y(q[random_bit])

    circ.cx(q[0],q[1])
    circ.cx(q[3],q[4])
    circ.cx(q[6],q[7])
    circ.cx(q[0],q[2])
    circ.cx(q[3],q[5])
    circ.cx(q[6],q[8])
    circ.ccx(q[1],q[2],q[0])
    circ.ccx(q[4],q[5],q[3])
    circ.ccx(q[7],q[8],q[6])
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.cx(q[0],q[3])
    circ.cx(q[0],q[6])
    circ.ccx(q[3],q[6],q[0])
    circ.measure(q,c)

    print(circ.draw())

    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

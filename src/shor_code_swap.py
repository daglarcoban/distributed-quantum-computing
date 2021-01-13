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

    #shor block section
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
    circ.h(q[0])
    circ.h(q[3])
    circ.h(q[6])
    circ.barrier()

    #cnot-small section 2
    for i in (0,3,6):
        circ.cnot(q[1+i],q[0+i])
        circ.swap()
    circ.barrier()






    print("Circuit depth: ", circ.depth())
    print(circ.draw())

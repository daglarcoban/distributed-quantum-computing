import numpy as np
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute
from quantuminspire.qiskit import QI
from src.util.authentication import QI_authenticate
from src.util.cat_disentangler import get_cat_disentangler
from src.util.cat_entangler import get_cat_entangler

if __name__ == '__main__':
    q=QuantumRegister(15)
    circ=QuantumCircuit(q)
    c = [ClassicalRegister(1) for _ in range(15)]
    for reg in c:
        circ.add_register(reg)
    #Initialize the main qubit that will be error corrected
    alpha = 1/np.sqrt(2)
    beta = 1/np.sqrt(2)
    circ.initialize([alpha, beta], q[0])
    
    #First part of the phase flip code
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    
    #CNOT from 1-7
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])
    circ.cx(q[11],q[10])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])

    circ.h(q[0])
    circ.h(q[5])
    circ.h(q[10])

    #First part of the bit flip code
    circ.cx(q[0],q[2])
    circ.cx(q[5],q[7])
    circ.cx(q[10],q[12])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    circ.cx(q[4],q[3])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    circ.cx(q[9],q[8])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    circ.cx(q[14],q[13])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    
    #Quantum error channel which generates a bit or phase flip error or both in one of the qubits
    random_bit = np.random.choice([0,2,3,5,7,8,10,12,13])
    RNG=np.random.random(1)
    if RNG>=0.66:
        circ.z(q[random_bit])
    elif RNG>=0.33 and RNG<0.66:
        circ.x(q[random_bit])
    else:
        circ.y(q[random_bit])
    
    #Second part of the bit flip code
    circ.cx(q[0],q[2])
    circ.cx(q[5],q[7])
    circ.cx(q[10],q[12])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    circ.cx(q[4],q[3])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[4]], [c[0][0], c[1][0], c[4][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    circ.cx(q[9],q[8])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[9]], [c[5][0], c[6][0], c[9][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    circ.cx(q[14],q[13])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[14]], [c[10][0], c[11][0], c[14][0]])
    

    circ.h(q[0])
    circ.h(q[5])
    circ.h(q[10])
    
    circ.cx(q[2],q[0])
    circ.cx(q[7],q[5])
    circ.cx(q[12],q[10])
    
    circ.tdg(q[0])
    circ.tdg(q[5])
    circ.tdg(q[10])
    
    circ=circ.compose(get_cat_entangler(2), [q[3], q[4], q[1]], [c[3][0], c[4][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[3], q[4], q[1]], [c[3][0], c[4][0], c[1][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[8], q[9], q[6]], [c[8][0], c[9][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[8], q[9], q[6]], [c[8][0], c[9][0], c[6][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[13], q[14], q[11]], [c[13][0], c[14][0], c[11][0]])
    circ.cx(q[11],q[10])
    circ = circ.compose(get_cat_disentangler(2), [q[13], q[14], q[11]], [c[13][0], c[14][0], c[11][0]])
    
    circ.t(q[0])
    circ.t(q[5])
    circ.t(q[10])
    
    circ.cx(q[2],q[0])
    circ.cx(q[7],q[5])
    circ.cx(q[12],q[10])
    
    circ.tdg(q[0])
    circ.tdg(q[5])
    circ.tdg(q[10])
    
    circ=circ.compose(get_cat_entangler(2), [q[3], q[4], q[1]], [c[3][0], c[4][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[3], q[4], q[1]], [c[3][0], c[4][0], c[1][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[8], q[9], q[6]], [c[8][0], c[9][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[8], q[9], q[6]], [c[8][0], c[9][0], c[6][0]])
    
    circ=circ.compose(get_cat_entangler(2), [q[13], q[14], q[11]], [c[13][0], c[14][0], c[11][0]])
    circ.cx(q[11],q[10])
    circ = circ.compose(get_cat_disentangler(2), [q[13], q[14], q[11]], [c[13][0], c[14][0], c[11][0]])
        
    circ.t(q[0])
    circ.t(q[2])
    circ.t(q[5])
    circ.t(q[7])
    circ.t(q[10])
    circ.t(q[12])
    
    circ.h(q[0])
    circ.cx(q[3],q[2])
    circ.h(q[5])
    circ.cx(q[8],q[7])
    circ.h(q[10])
    circ.cx(q[13],q[12])
    
    circ.tdg(q[2])
    circ.t(q[3])
    circ.tdg(q[7])
    circ.t(q[8])
    circ.tdg(q[12])
    circ.t(q[13])
    
    circ.cx(q[3],q[2])
    circ.cx(q[8],q[7])
    circ.cx(q[13],q[12])
    
    #Second part of the phase flip code
    circ.h(q[0])
    circ.h(q[5])
    circ.h(q[10])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[6]], [c[0][0], c[1][0], c[6][0]])
    
    #
    circ=circ.compose(get_cat_entangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])
    circ.cx(q[11],q[10])
    circ = circ.compose(get_cat_disentangler(2), [q[0], q[1], q[11]], [c[0][0], c[1][0], c[11][0]])
    
    #Final Toffoli gate
    circ.h(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    
    circ.tdg(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    
    circ.t(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[5], q[6], q[1]], [c[5][0], c[6][0], c[1][0]])
    
    circ.tdg(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    circ.cx(q[1],q[0])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[1]], [c[10][0], c[11][0], c[1][0]])
    
    circ.t(q[0])
    circ.t(q[5])
    
    circ.h(q[0])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])
    
    circ.tdg(q[5])
    circ.t(q[10])
    
    circ=circ.compose(get_cat_entangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])
    circ.cx(q[6],q[5])
    circ = circ.compose(get_cat_disentangler(2), [q[10], q[11], q[6]], [c[10][0], c[11][0], c[6][0]])

    print(circ.draw())
    print("Circuit depth: ", circ.depth()) #measure at the end + error block (which might introduce extra gate) should be commented out

    # measure all so we can see results
    for i in range(15):
        circ.measure(circ.qregs[0][i], circ.cregs[i])

    #print results
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circ, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circ)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

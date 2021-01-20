from math import sqrt
import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute

from quantuminspire.qiskit import QI

from src.util.authentication import QI_authenticate
from src.util.cat_disentangler import get_cat_disentangler
from src.util.cat_entangler import get_cat_entangler

# def toffoli(circuit_in=QuantumCircuit, control_1=int, control_2=int, q_in=int, q_reg=QuantumRegister):
#     circuit_in.h(q_reg[q_in])
#     circuit_in.cx(q_reg[control_2], q_reg[q_in])
#     circuit_in.tdg(q_reg[q_in])
#     circuit_in.cx(q_reg[control_1], q_reg[q_in])
#     circuit_in.t(q_reg[q_in])
#     circuit_in.cx(q_reg[control_2], q_reg[q_in])
#     circuit_in.tdg(q_reg[q_in])
#     circuit_in.cx(q_reg[control_1], q_reg[q_in])
#     circuit_in.t(q_reg[control_2])
#     circuit_in.t(q_reg[q_in])
#     circuit_in.cx(q_reg[control_1], q_reg[control_2])
#     circuit_in.h(q_reg[q_in])
#     circuit_in.t(q_reg[control_1])
#     circuit_in.tdg(q_reg[control_2])
#     circuit_in.cx(q_reg[control_1], q_reg[control_2])
#
#     return circuit_in


if __name__ == '__main__':
    c_a = [ClassicalRegister(1) for _ in range(4)]
    c_b = [ClassicalRegister(1) for _ in range(4)]
    c_c = [ClassicalRegister(1) for _ in range(4)]
    q_a = QuantumRegister(4)
    q_b = QuantumRegister(4)
    q_c = QuantumRegister(4)
    q = [q_a, q_b, q_c]
    c = [c_a, c_b, c_c]

    circuit_a = QuantumCircuit(q_a)
    for reg in c_a:
        circuit_a.add_register(reg)
    circuit_b = QuantumCircuit(q_b)
    for reg in c_b:
        circuit_b.add_register(reg)
    circuit_c = QuantumCircuit(q_c)
    for reg in c_c:
        circuit_c.add_register(reg)

    # Initialize the main qubit that will be error corrected
    alpha =  0 #/ sqrt(2)
    beta = 1 #/ sqrt(2)
    circuit_a.initialize([alpha, beta], q_a[0])

    circuit = circuit_a + circuit_b + circuit_c

    # Channel qubits are q_a[3], q_b[3], q_c[3]

    #First part of the phase flip code
    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[3], q_b[3]], [c_a[0][0], c_a[3][0], c_b[3][0]])
    circuit.cx(q_b[3], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[3], q_b[3]], [c_a[0][0], c_a[3][0], c_b[3][0]])

    circuit.barrier()  # until first cnot between 1 and 4

    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[3], q_c[3]], [c_a[0][0], c_a[3][0], c_c[3][0]])
    circuit.cx(q_c[3], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[3], q_c[3]], [c_a[0][0], c_a[3][0], c_c[3][0]])

    circuit.barrier()  # until second cnot between 1 and 7

    circuit.h(q_a[0])
    circuit.h(q_b[0])
    circuit.h(q_c[0])

    # First part of the bit flip code
    circuit.cx(q_a[0], q_a[1])
    circuit.cx(q_a[0], q_a[2])
    circuit.cx(q_b[0], q_b[1])
    circuit.cx(q_b[0], q_b[2])
    circuit.cx(q_c[0], q_c[1])
    circuit.cx(q_c[0], q_c[2])

    circuit.barrier()  # until ERROR BLOCK

    ### ERROR BLOCK --- START
    random_bit = np.random.choice([0, 1, 2])
    random_cluster = np.random.choice([0, 1, 2])
    error = np.random.random(1)

    if error >= 0.66:
        circuit.z(q[random_cluster][random_bit])
    elif error >= 0.33 and error < 0.66:
        circuit.x(q[random_cluster][random_bit])
    else:
        circuit.y(q[random_cluster][random_bit])
    ## ERROR BLOCK --- END

    circuit.barrier()  # after ERROR BLOCK

    #Second part of the bit flip code
    circuit.cx(q_a[0], q_a[1])
    circuit.cx(q_a[0], q_a[2])
    circuit.cx(q_b[0], q_b[1])
    circuit.cx(q_b[0], q_b[2])
    circuit.cx(q_c[0], q_c[1])
    circuit.cx(q_c[0], q_c[2])


    circuit.ccx(q_a[1],q_a[2],q_a[0])
    circuit.ccx(q_b[1], q_b[2], q_b[0])
    circuit.ccx(q_c[1], q_c[2], q_c[0])

    circuit.barrier()  # until H gates

    #Second part of the phase flip code
    circuit.h(q_a[0])
    circuit.h(q_b[0])
    circuit.h(q_c[0])

    circuit.barrier()  # until non local gates

    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[3], q_b[3]], [c_a[0][0], c_a[3][0], c_b[3][0]])
    circuit.cx(q_b[3], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[3], q_b[3]], [c_a[0][0], c_a[3][0], c_b[3][0]])

    circuit.barrier()  # until first cnot between 1 and 4

    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[3], q_c[3]], [c_a[0][0], c_a[3][0], c_c[3][0]])
    circuit.cx(q_c[3], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[3], q_c[3]], [c_a[0][0], c_a[3][0], c_c[3][0]])

    circuit.barrier()  # until non local toffoli

    ### NON LOCAL TOFFOLI GATE --- START
    circuit.h(q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[3], q_a[3]], [c_c[0][0], c_c[3][0], c_a[3][0]])
    circuit.cx(q_a[3], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[3], q_a[3]], [c_c[0][0], c_c[3][0], c_a[3][0]])

    circuit.tdg(q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[3], q_a[3]], [c_b[0][0], c_b[3][0], c_a[3][0]])
    circuit.cx(q_a[3], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[3], q_a[3]], [c_b[0][0], c_b[3][0], c_a[3][0]])

    circuit.t(q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[3], q_a[3]], [c_c[0][0], c_c[3][0], c_a[3][0]])
    circuit.cx(q_a[3], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[3], q_a[3]], [c_c[0][0], c_c[3][0], c_a[3][0]])

    circuit.tdg(q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[3], q_a[3]], [c_b[0][0], c_b[3][0], c_a[3][0]])
    circuit.cx(q_a[3], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[3], q_a[3]], [c_b[0][0], c_b[3][0], c_a[3][0]])

    circuit.t(q_c[0])
    circuit.t(q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[3], q_c[3]], [c_b[0][0], c_b[3][0], c_c[3][0]])
    circuit.cx(q_c[3], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[3], q_c[3]], [c_b[0][0], c_b[3][0], c_c[3][0]])

    circuit.h(q_a[0])
    circuit.t(q_b[0])
    circuit.tdg(q_c[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[3], q_c[3]], [c_b[0][0], c_b[3][0], c_c[3][0]])
    circuit.cx(q_c[3], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[3], q_c[3]], [c_b[0][0], c_b[3][0], c_c[3][0]])
    ## NON LOCAL TOFFOLI GATE --- END

    print(circuit.draw())
    print("Circuit depth: ", circuit.depth()) #measure at the end + error block (which might introduce extra gate) should be commented out

    for i in range(3):
        for j in range(4):
            circuit.measure(circuit.qregs[i][j], circuit.cregs[4*i + j])

    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circuit, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circuit)
    print('State\tCounts')

    #Delete channel qubits from bit string to be printed
    for state, counts in histogram.items():
        results_all = list(list(state))
        results_all = results_all[::2]
        results_all = "".join(results_all)
        results = []
        for i in range(len(results_all)):
            if i % 4 == 0:
                continue
            else:
                results.append(results_all[i])
        results = "".join(results)
        results = results + " " + str(counts)
        print(results)

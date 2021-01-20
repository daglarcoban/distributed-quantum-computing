from math import sqrt
import numpy as np
import time

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute, BasicAer

from quantuminspire.qiskit import QI

from src.util.authentication import QI_authenticate
from src.util.cat_disentangler import get_cat_disentangler
from src.util.cat_entangler import get_cat_entangler


if __name__ == '__main__':
    start_time = time.time()

    c_a = [ClassicalRegister(1) for _ in range(5)]
    c_b = [ClassicalRegister(1) for _ in range(5)]
    c_c = [ClassicalRegister(1) for _ in range(5)]
    c_d = [ClassicalRegister(1) for _ in range(5)]
    q_a = QuantumRegister(5)
    q_b = QuantumRegister(5)
    q_c = QuantumRegister(5)
    q_d = QuantumRegister(5)
    q = [q_a, q_b, q_c, q_d]
    c = [c_a, c_b, c_c, c_d]

    circuit_a = QuantumCircuit(q_a)
    for reg in c_a:
        circuit_a.add_register(reg)
    circuit_b = QuantumCircuit(q_b)
    for reg in c_b:
        circuit_b.add_register(reg)
    circuit_c = QuantumCircuit(q_c)
    for reg in c_c:
        circuit_c.add_register(reg)
    circuit_d = QuantumCircuit(q_d)
    for reg in c_d:
        circuit_d.add_register(reg)

    alpha = 0 # / sqrt(2)
    beta = 1 #/ sqrt(2)
    circuit_a.initialize([alpha, beta], q_a[0])

    circuit = circuit_a + circuit_b + circuit_c + circuit_d

    # Channel qubits are q_a[4], q_b[4], q_c[4], q_d[4]

    # cnot with cluster a and b
    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[4], q_b[4]], [c_a[0][0], c_a[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[4], q_b[4]], [c_a[0][0], c_a[4][0], c_b[4][0]])

    circuit.barrier()

    # cnot with cluster a and c
    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[4], q_c[4]], [c_a[0][0], c_a[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[4], q_c[4]], [c_a[0][0], c_a[4][0], c_c[4][0]])

    circuit.barrier()

    # cnot with cluster a and d
    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[4], q_d[4]], [c_a[0][0], c_a[4][0], c_d[4][0]])
    circuit.cx(q_d[4], q_d[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[4], q_d[4]], [c_a[0][0], c_a[4][0], c_d[4][0]])

    circuit.barrier()

    circuit.h(q_a[0])
    circuit.h(q_b[0])
    circuit.h(q_c[0])
    circuit.h(q_d[0])

    circuit.cx(q_a[0], q_a[1])
    circuit.cx(q_a[0], q_a[2])
    circuit.cx(q_a[0], q_a[3])
    circuit.cx(q_b[0], q_b[1])
    circuit.cx(q_b[0], q_b[2])
    circuit.cx(q_b[0], q_b[3])
    circuit.cx(q_c[0], q_c[1])
    circuit.cx(q_c[0], q_c[2])
    circuit.cx(q_c[0], q_c[3])

    circuit.barrier()  # until ERROR BLOCK

    ### ERROR BLOCK --- START
    random_bit = np.random.choice([0, 1, 2, 3])
    random_cluster = np.random.choice([0, 1, 2, 3])
    error = np.random.random(1)

    if error >= 0.66:
        circuit.z(q[random_cluster][random_bit])
    elif error >= 0.33 and error < 0.66:
        circuit.x(q[random_cluster][random_bit])
    else:
        circuit.y(q[random_cluster][random_bit])
    ## ERROR BLOCK --- END

    circuit.barrier()  # after ERROR BLOCK

    circuit.cx(q_a[0], q_a[1])
    circuit.cx(q_a[0], q_a[2])
    circuit.cx(q_a[0], q_a[3])
    circuit.cx(q_b[0], q_b[1])
    circuit.cx(q_b[0], q_b[2])
    circuit.cx(q_b[0], q_b[3])
    circuit.cx(q_c[0], q_c[1])
    circuit.cx(q_c[0], q_c[2])
    circuit.cx(q_c[0], q_c[3])

    circuit.mct([q_a[1], q_a[2], q_a[3]], q_a[0], None, mode="advanced")
    circuit.mct([q_b[1], q_b[2], q_b[3]], q_b[0], None, mode="advanced")
    circuit.mct([q_c[1], q_c[2], q_c[3]], q_c[0], None, mode="advanced")
    circuit.mct([q_d[1], q_d[2], q_d[3]], q_d[0], None, mode="advanced")

    circuit.barrier()  # until h gates

    circuit.h(q_a[0])
    circuit.h(q_b[0])
    circuit.h(q_c[0])
    circuit.h(q_d[0])

    circuit.barrier()

    #NON LOCAL CNOT STUFF

    # cnot with cluster a and b
    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[4], q_b[4]], [c_a[0][0], c_a[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[4], q_b[4]], [c_a[0][0], c_a[4][0], c_b[4][0]])

    circuit.barrier()

    # cnot with cluster a and c
    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[4], q_c[4]], [c_a[0][0], c_a[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[4], q_c[4]], [c_a[0][0], c_a[4][0], c_c[4][0]])

    circuit.barrier()

    # cnot with cluster a and d
    circuit = circuit.compose(get_cat_entangler(2), [q_a[0], q_a[4], q_d[4]], [c_a[0][0], c_a[4][0], c_d[4][0]])
    circuit.cx(q_d[4], q_d[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_a[0], q_a[4], q_d[4]], [c_a[0][0], c_a[4][0], c_d[4][0]])

    circuit.barrier()


    ### NON LOCAL CCCX GATES --- START

    ##FIRST NORMAL TOFFOLI
    circuit.h(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])

    circuit.tdg(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])

    circuit.t(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])

    circuit.tdg(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])

    circuit.t(q_b[0])
    circuit.t(q_c[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])

    circuit.h(q_b[0])
    circuit.t(q_d[0])
    circuit.tdg(q_c[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])


    # FIRST NON LOCAL TOFFOLI END!!!

    circuit.h(q_a[0])
    circuit.tdg(q_b[0])
    circuit.tdg(q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])

    circuit.t(q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])

    circuit.h(q_a[0])

    ## SECOND NON LOCAL TOFFOLI
    circuit.h(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])

    circuit.tdg(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])

    circuit.t(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_b[4]], [c_c[0][0], c_c[4][0], c_b[4][0]])

    circuit.tdg(q_b[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])
    circuit.cx(q_b[4], q_b[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_b[4]], [c_d[0][0], c_d[4][0], c_b[4][0]])

    circuit.t(q_b[0])
    circuit.t(q_c[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])

    circuit.h(q_b[0])
    circuit.t(q_d[0])
    circuit.tdg(q_c[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    ## SECOND NON LCOAL TOFFOLI END
    circuit.h(q_a[0])
    circuit.tdg(q_b[0])
    circuit.tdg(q_a[0])
    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])
    circuit.t(q_a[0])
    circuit = circuit.compose(get_cat_entangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_b[0], q_b[4], q_a[4]], [c_b[0][0], c_b[4][0], c_a[4][0]])
    circuit.h(q_a[0])


    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.h(q_a[0])

    circuit.rz(-1/8 * np.pi, q_c[0])
    circuit.rz(-1/8 * np.pi, q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])

    circuit.rz(1 / 8 * np.pi, q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])

    circuit.h(q_a[0])
    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.cx(q_c[4], q_c[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_c[4]], [c_d[0][0], c_d[4][0], c_c[4][0]])
    circuit.h(q_a[0])

    circuit.rz(1/8 * np.pi, q_c[0])
    circuit.rz(1/8 * np.pi, q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])

    circuit.rz(-1 / 8 * np.pi, q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_c[0], q_c[4], q_a[4]], [c_c[0][0], c_c[4][0], c_a[4][0]])
    circuit.h(q_a[0])
    circuit.h(q_a[0])
    circuit.rz(1/8 * np.pi, q_d[0])
    circuit.rz(1/8 * np.pi, q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_a[4]], [c_d[0][0], c_d[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_a[4]], [c_d[0][0], c_d[4][0], c_a[4][0]])

    circuit.rz(-1 / 8 * np.pi, q_a[0])

    circuit = circuit.compose(get_cat_entangler(2), [q_d[0], q_d[4], q_a[4]], [c_d[0][0], c_d[4][0], c_a[4][0]])
    circuit.cx(q_a[4], q_a[0])
    circuit = circuit.compose(get_cat_disentangler(2), [q_d[0], q_d[4], q_a[4]], [c_d[0][0], c_d[4][0], c_a[4][0]])

    circuit.h(q_a[0])
    ## NON LOCAL CCCX GATES --- END

    # print(circuit.draw())
    print("Circuit depth: ", circuit.depth()) #measure at the end + error block (which might introduce extra gate) should be commented out

    for i in range(4):
        for j in range(5):
            circuit.measure(circuit.qregs[i][j], circuit.cregs[5*i + j])

    # QI_authenticate()
    # qi_backend = QI.get_backend('QX single-node simulator')
    # qi_job = execute(circuit, backend=qi_backend, shots=1)
    # qi_result = qi_job.result()
    # histogram = qi_result.get_counts(circuit)
    # print('State\tCounts')

    print("\nResult from the local Qiskit simulator backend:\n")
    backend = BasicAer.get_backend("qasm_simulator")
    job = execute(circuit, backend=backend, shots=64)
    result = job.result()
    print(result.get_counts(circuit))

    print("--- %s minutes ---" % ((time.time() - start_time) / 60))

    #
    # #Delete channel qubits from bit string to be printed
    # for state, counts in histogram.items():
    #     results_all = list(list(state))
    #     results_all = results_all[::2]
    #     results_all = "".join(results_all)
    #     results = []
    #     for i in range(len(results_all)):
    #         if i % 5 == 0:
    #             continue
    #         else:
    #             results.append(results_all[i])
    #     results = "".join(results)
    #     results = results + " " + str(counts)
    #     print(results)

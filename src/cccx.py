import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import execute, Aer

from quantuminspire.qiskit import QI

from src.util.authentication import QI_authenticate

def cccx(circuit, control_qubit_1, control_qubit_2, control_qubit_3, target_qubit):
    circuit.ccx(control_qubit_1, control_qubit_2, control_qubit_3)
    circuit.h(target_qubit)
    circuit.tdg(control_qubit_3)
    circuit.tdg(target_qubit)
    circuit.cx(control_qubit_3, target_qubit)
    circuit.t(target_qubit)
    circuit.cx(control_qubit_3, target_qubit)
    circuit.h(target_qubit)
    circuit.ccx(control_qubit_1, control_qubit_2, control_qubit_3)
    circuit.h(target_qubit)
    circuit.t(control_qubit_3)
    circuit.t(target_qubit)
    circuit.cx(control_qubit_3, target_qubit)
    circuit.tdg(target_qubit)
    circuit.cx(control_qubit_3, target_qubit)
    circuit.h(target_qubit)
    circuit.cx(control_qubit_1, control_qubit_2)
    circuit.h(target_qubit)
    circuit.rz(-1/8 * np.pi, control_qubit_2)
    circuit.rz(-1/8 * np.pi, target_qubit)
    circuit.cx(control_qubit_2, target_qubit)
    circuit.rz(1 / 8 * np.pi, target_qubit)
    circuit.cx(control_qubit_2, target_qubit)
    circuit.h(target_qubit)
    circuit.cx(control_qubit_1, control_qubit_2)
    circuit.h(target_qubit)
    circuit.rz(1/8 * np.pi, control_qubit_2)
    circuit.rz(1/8 * np.pi, target_qubit)
    circuit.cx(control_qubit_2, target_qubit)
    circuit.rz(-1 / 8 * np.pi, target_qubit)
    circuit.cx(control_qubit_2, target_qubit)
    circuit.h(target_qubit)
    circuit.h(target_qubit)
    circuit.rz(1/8 * np.pi, control_qubit_1)
    circuit.rz(1/8 * np.pi, target_qubit)
    circuit.cx(control_qubit_1, target_qubit)
    circuit.rz(-1 / 8 * np.pi, target_qubit)
    circuit.cx(control_qubit_1, target_qubit)
    circuit.h(target_qubit)
    pass


if __name__ == '__main__':
    c = ClassicalRegister(4)
    q = QuantumRegister(4)
    circuit = QuantumCircuit(q, c)

    # circuit.ccx(q[0], q[1], q[2])
    # circuit.h(q[3])
    # circuit.tdg(q[2])
    # circuit.tdg(q[3])
    # circuit.cx(q[2], q[3])
    # circuit.t(q[3])
    # circuit.cx(q[2], q[3])
    # circuit.h(q[3])
    # circuit.ccx(q[0], q[1], q[2])
    # circuit.h(q[3])
    # circuit.t(q[2])
    # circuit.t(q[3])
    # circuit.cx(q[2], q[3])
    # circuit.tdg(q[3])
    # circuit.cx(q[2], q[3])
    # circuit.h(q[3])
    # circuit.cx(q[0], q[1])
    # circuit.h(q[3])
    # circuit.rz(-1/8 * np.pi, q[1])
    # circuit.rz(-1/8 * np.pi, q[3])
    # circuit.cx(q[1], q[3])
    # circuit.rz(1 / 8 * np.pi, q[3])
    # circuit.cx(q[1], q[3])
    # circuit.h(q[3])
    # circuit.cx(q[0], q[1])
    # circuit.h(q[3])
    # circuit.rz(1/8 * np.pi, q[1])
    # circuit.rz(1/8 * np.pi, q[3])
    # circuit.cx(q[1], q[3])
    # circuit.rz(-1 / 8 * np.pi, q[3])
    # circuit.cx(q[1], q[3])
    # circuit.h(q[3])
    # circuit.h(q[3])
    # circuit.rz(1/8 * np.pi, q[0])
    # circuit.rz(1/8 * np.pi, q[3])
    # circuit.cx(q[0], q[3])
    # circuit.rz(-1 / 8 * np.pi, q[3])
    # circuit.cx(q[0], q[3])
    # circuit.h(q[3])
    cccx(circuit,q[0],q[1],q[2],q[3])

    print(circuit.draw())

    # backend = Aer.get_backend('unitary_simulator')
    # job = execute(circuit, backend)
    # result = job.result()
    # print(np.trace(np.around(result.get_unitary(circuit), 1)))

    # measure all so we can see results
    circuit.measure(q, c)


    # print results
    QI_authenticate()
    qi_backend = QI.get_backend('QX single-node simulator')
    qi_job = execute(circuit, backend=qi_backend, shots=256)
    qi_result = qi_job.result()
    histogram = qi_result.get_counts(circuit)
    print('State\tCounts')
    [print('{0}\t{1}'.format(state, counts)) for state, counts in histogram.items()]

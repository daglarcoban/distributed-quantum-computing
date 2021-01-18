from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit, execute
from quantuminspire.qiskit import QI

from src.shor_code_variants.shor_code_normal import get_shor_code_normal_circuit
from src.util.authentication import QI_authenticate

def test_shor_code_normal():
    for init_state in [0, 1]:
    # Superpositions hard to check in a automated way because of the non-determinism
    # But these can just be tested manually in the corresponding files,
    # as well as introducing a random error on a random bit
        for bit in range(9):
            for error in ['x', 'y', 'z', None]:     #Also check correct working without error (None)
                c = ClassicalRegister(9)
                q = QuantumRegister(9)
                circ = QuantumCircuit(q, c)

                alpha = (1 + init_state) % 2
                beta = init_state
                circ.initialize([alpha, beta], q[0])

                circ = circ.compose(get_shor_code_normal_circuit(error, bit), range(9))

                #measure all so we can see results
                circ.measure(q, c)

                #print results
                QI_authenticate()
                qi_backend = QI.get_backend('QX single-node simulator')
                qi_job = execute(circ, backend=qi_backend, shots=256)
                qi_result = qi_job.result()
                histogram = qi_result.get_counts(circ)
                result_state = list(histogram.items())[0][0]
                #We only care about the first bit (or last when printed in qiskit)
                #We want to know if this is corrected properly/has remained the same
                result_first_bit = result_state[-1]
                if result_first_bit == str(init_state):
                    print("CORRECT")
                else:
                    print("WRONG")
                #Maybe convert to pytest file instead of printing? :P

if __name__ == '__main__':
    test_shor_code_normal()
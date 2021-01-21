import warnings

from qiskit import execute
from quantuminspire.qiskit import QI

from src.shor_code_variants.linear_nearest_neighbour.shor_code_lnn_swaps import get_shor_code_lnn_swaps
from src.shor_code_variants.n_clusters_of_n.shor_code_4_clusters_of_4 import get_shor_code_4_c_4
from src.shor_code_variants.shor_code_normal import get_shor_code_normal_circuit
from src.shor_code_variants.linear_nearest_neighbour.shor_code_lnn_combined import get_shor_code_lnn_combined
from src.shor_code_variants.linear_nearest_neighbour.shor_code_lnn_non_local import get_shor_code_lnn_non_local
from src.shor_code_variants.n_clusters_of_n.shor_code_3_clusters_of_3 import get_shor_code_3_c_3
from src.util.authentication import QI_authenticate

import unittest


# Superpositions hard to check in a automated way because of the non-determinism
# But these can just be tested manually in the corresponding files,
# as well as introducing a random error on a random bit

# Also check correct working without error (None)

# For the assertion, we only care about the first bit (or last when printed in qiskit)
# We want to know if this is corrected properly/has remained the same

class Test(unittest.TestCase):
    SHOTS = 8

    def test_normal(self):
        print("Testing normal shore code")
        print("-------------------------")
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        for init_state in [0, 1]:
            for bit in range(9):
                for error in ['x', 'y', 'z', None]:
                    alpha = (1 + init_state) % 2
                    beta = init_state
                    print("init state: {}, bit: {}, error: {}".format(init_state, bit, error))

                    circ = get_shor_code_normal_circuit(error, bit, alpha, beta)

                    QI_authenticate()
                    qi_backend = QI.get_backend('QX single-node simulator')
                    qi_job = execute(circ, backend=qi_backend, shots=self.SHOTS)
                    qi_result = qi_job.result()
                    histogram = qi_result.get_counts(circ)
                    result_state = list(histogram.items())[0][0]

                    result_first_bit = result_state[-1]
                    result = result_first_bit == str(init_state)
                    print(result)
                    print("-------------------------")
                    self.assertTrue(result)

    def test_lnn_combined(self):
        print("Testing lnn combined shore code")
        print("-------------------------")
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        for init_state in [0, 1]:
            for bit in range(9):
                for error in ['x', 'y', 'z', None]:
                    alpha = (1 + init_state) % 2
                    beta = init_state
                    print("init state: {}, bit: {}, error: {}".format(init_state, bit, error))

                    circ = get_shor_code_lnn_combined(error, bit, alpha, beta)

                    QI_authenticate()
                    qi_backend = QI.get_backend('QX single-node simulator')
                    qi_job = execute(circ, backend=qi_backend, shots=self.SHOTS)
                    qi_result = qi_job.result()
                    histogram = qi_result.get_counts(circ)
                    result_state = list(histogram.items())[0][0]

                    result_first_bit = result_state[-1]
                    result = result_first_bit == str(init_state)
                    print(result)
                    print("-------------------------")
                    self.assertTrue(result)

    def test_lnn_non_local(self):
        print("Testing lnn non local shore code")
        print("-------------------------")
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        for init_state in [0, 1]:
            for bit in range(9):
                for error in ['x', 'y', 'z', None]:
                    alpha = (1 + init_state) % 2
                    beta = init_state
                    print("init state: {}, bit: {}, error: {}".format(init_state, bit, error))

                    circ = get_shor_code_lnn_non_local(error, bit, alpha, beta)

                    QI_authenticate()
                    qi_backend = QI.get_backend('QX single-node simulator')
                    qi_job = execute(circ, backend=qi_backend, shots=self.SHOTS)
                    qi_result = qi_job.result()
                    histogram = qi_result.get_counts(circ)
                    result_state = list(histogram.items())[0][0]

                    result_first_bit = result_state[-1]
                    result = result_first_bit == str(init_state)
                    print(result)
                    print("-------------------------")
                    self.assertTrue(result)

    def test_lnn_swaps(self):
        print("Testing lnn swaps shore code")
        print("-------------------------")
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        for init_state in [0, 1]:
            for bit in range(9):
                for error in ['x', 'y', 'z', None]:
                    alpha = (1 + init_state) % 2
                    beta = init_state
                    print("init state: {}, bit: {}, error: {}".format(init_state, bit, error))

                    circ = get_shor_code_lnn_swaps(error, bit, alpha, beta)

                    QI_authenticate()
                    qi_backend = QI.get_backend('QX single-node simulator')
                    qi_job = execute(circ, backend=qi_backend, shots=self.SHOTS)
                    qi_result = qi_job.result()
                    histogram = qi_result.get_counts(circ)
                    result_state = list(histogram.items())[0][0]

                    result_first_bit = result_state[-1]
                    result = result_first_bit == str(init_state)
                    print(result)
                    print("-------------------------")
                    self.assertTrue(result)

    def test_3_cluster(self):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        print("Testing 3 clusters of 3 shor code")
        print("-------------------------")
        for init_state in [0, 1]:
            for bit in range(3):
                for error in ['x', 'y', 'z', None]:
                    for cluster in [0, 1, 2]:
                        print("init state: {}, bit: {}, error: {}, cluster: {}".format(init_state, bit, error, cluster))

                        alpha = (1 + init_state) % 2
                        beta = init_state

                        circ = get_shor_code_3_c_3(cluster, error, bit, alpha, beta)

                        QI_authenticate()
                        qi_backend = QI.get_backend('QX single-node simulator')
                        qi_job = execute(circ, backend=qi_backend, shots=self.SHOTS)
                        qi_result = qi_job.result()
                        histogram = qi_result.get_counts(circ)
                        result_state = list(histogram.items())[0][0]

                        result_first_bit = result_state[-1]
                        print(result_first_bit == str(init_state))
                        print("-------------------------")
                        self.assertEqual(result_first_bit, str(init_state))

    # def test_4_cluster(self):
    #     print("Testing 4 clusters of 4 shor code")
    #     print("-------------------------")
    #     warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
    #     for init_state in [0, 1]:
    #         for bit in range(4):
    #             for error in ['x', 'y', 'z', None]:
    #                 for cluster in [0, 1, 2, 3]:
    #
    #                     print("init state: {}, bit: {}, error: {}, cluster: {}".format(init_state, bit, error, cluster))
    #
    #                     alpha = (1 + init_state) % 2
    #                     beta = init_state
    #
    #                     circ = get_shor_code_4_c_4(cluster, error, bit, alpha, beta)
    #
    #                     QI_authenticate()
    #                     qi_backend = QI.get_backend('QX single-node simulator')
    #                     qi_job = execute(circ, backend=qi_backend, shots=self.SHOTS)
    #                     qi_result = qi_job.result()
    #                     histogram = qi_result.get_counts(circ)
    #                     result_state = list(histogram.items())[0][0]

    #                     result_first_bit = result_state[-1]
    #                     print(result_first_bit == str(init_state))
    #                     print("-------------------------")
    #                     self.assertEqual(result_first_bit, str(init_state))


if __name__ == '__main__':
    unittest.main()

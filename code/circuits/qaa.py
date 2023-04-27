import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info.operators import Operator

from code.circuits.oracle import Oracle
from code.circuits.tnn import TNN


def get_diffusion_operator(ora: Oracle, tun_net: TNN, k_0: int):
    """
    Function to generate the diffusion operator corresponding to the query oracle and the tunable network in its current state.

    Arguments:
        - ora: Oracle, the query oracle
        - tun_net: TNN, the tunable neural network

    Returns:
        The quantum gate representing the diffusion operator
    """
    n = tun_net.dim
    qc = QuantumCircuit(n+2)
    # Chi_g
    qc.cz(n, n+1)
    # A^-1
    qc.cry(-np.pi/(2*k_0+1), n, n+1)
    qc.append(tun_net.network, range(n+1))
    qc.append(ora.inv_gate, range(n+1))
    # -Chi_0
    mat = -np.eye(2**(n+2))
    mat[0,0] = 1
    op = Operator(mat)
    qc.unitary(op, range(n+2), label="Chi_0")
    # A
    qc.append(ora.gate, range(n+1))
    qc.append(tun_net.network, range(n+1))
    qc.cry(np.pi/(2*k_0+1), n, n+1)
    return qc.to_gate(label="Diffusion")
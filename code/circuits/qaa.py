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


def get_diffusion_from_density(density, tun_net: TNN, k_0: int):
    n = tun_net.dim
    qc = QuantumCircuit(n+2)
    # Chi_g
    qc.cz(n, n+1)
    # A^-1
    qc.cry(-np.pi/(2*k_0+1), n, n+1)
    qc.append(tun_net.network, range(n+1))
    # -Chi_0
    mat = 2*density - np.eye(2**(n+2))
    op = Operator(mat)
    qc.unitary(op, range(n+2), label="Chi_0")
    # A
    qc.append(tun_net.network, range(n+1))
    qc.cry(np.pi/(2*k_0+1), n, n+1)
    return qc.to_gate(label="Diffusion")
    

def get_chi_k(n: int, k: int):
    mat = np.eye(2**n)
    for i in range(2**n):
        if format(i,"0b").count("1") <= k:
            mat[i,i] = -1

    return mat

def get_diffusion_k(density, n: int, k: int):
    mat_chi_k = np.eye(2**n)
    for i in range(2**n):
        if format(i,"0b").count("1") <= k:
            mat_chi_k[i,i] = -1
    op_chi_k = Operator(mat_chi_k)

    mat_chi_0 = 2*density - np.eye(2**(n+2))
    op_chi_0 = Operator(mat_chi_0)
    
    qc = QuantumCircuit(n+2)
    qc.append(op_chi_k, range(n))
    qc.append(op_chi_0, range(n+2))

    return qc.to_gate(label=f"Diffusion Hamming <= {k}")



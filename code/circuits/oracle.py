import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info.operators import Operator


class Oracle:

    def __init__(self, n: int, logic: str):
        """
        Instanciates an object of the Oracle class which is the query oracle
        for the target function.

        Arguments:
            - n: int, the dimension of the input space
            - logic: str, corresponding to the truth table of the target function

        Returns:
            - An object of the class Oracle with attributes:
                * dim: the dimension of the input space
                * logic: the string corresponding to the truth table
                * gate: the quantum gate corresponding to the oracle
                * inv_gate: the inverse of gate
        """
        if len(logic) != 2**n:
            raise ValueError(f"The length of gates is {len(logic)}, it should be {2**n}")
        
        self.dim = n
        self.logic = logic

        function_gate = self.__get_function_gate()

        qc = QuantumCircuit(n+1)
        qc.h(range(n))
        qc.append(function_gate, range(n+1))

        qc_inv = QuantumCircuit(n+1)
        qc_inv.append(function_gate, range(n+1))
        qc_inv.h(range(n))

        self.gate = qc.to_gate(label="Oracle")
        self.inv_gate = qc_inv.to_gate(label="Oracle^-1")

    
    def __get_function_gate(self):
        n = self.dim
        uni = np.eye(2**(n+1))

        for i in range(2**n):
            if self.logic[i] == "1":
                bin_i = np.binary_repr(i,n)
                col_num = int(bin_i[::-1],2)
                uni[:, [col_num, col_num+2**n]] = uni[:, [col_num+2**n, col_num]]
        
        return Operator(uni)




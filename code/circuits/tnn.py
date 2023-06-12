import numpy as np

import code.utilities.utility as util

from qiskit import QuantumCircuit


class TNN:

    def __init__(self, n: int, gates: dict={}):
        """
        Instanciates an object of the class TNN which is a tunable neural network.

        Arguments:
            - n: int, the dimension of the input space
            - gates: dict (default={}), the dictionary containing the state of all the possible gates of the tunable neural network

        Returns:
            - An object of the class TNN with attributes:
                * dim: the dimension of the input space
                * gates:  the dictionary containing the state of all the possible gates of the tunable neural network
                * network: the quantum gate corresponding to the tunable neural network
        """
        self.dim = n

        if gates == {}:
            gates = self.__generate_gates()
        elif len(gates) != 2**n:
            raise ValueError(f"The length of gates is {len(gates)}, it should be {n}")
        self.gates = gates

        self.generate_network()


    def __generate_gates(self):
        gates = {}
        for i in range(2**(self.dim)):
            gates[np.binary_repr(i,self.dim)] = 0
        return gates


    def generate_network(self):
        """
        Method of the TNN class to update the quantum gate corresponding to the current state of the network.
        """
        qc = QuantumCircuit(self.dim+1)
        for g in self.gates:
            if self.gates[g] == 1:
                controls = []
                for i in range(self.dim):
                    if g[i] == "1":
                        controls.append(i)
                if controls == []:
                    qc.x(self.dim)
                else:
                    qc.mcx(controls, self.dim)
        self.network = qc.to_gate(label="TNN")


    def update_tnn(self, to_update: list):
        """
        Method of the TNN class to update the gates attribute.

        Aguments:
            - to_update: list, the list of gates to be updated
        """
        for s in to_update:
            if s not in self.gates:
                raise ValueError(f"{s} is not a gate")
            else:
                self.gates[s] = (self.gates[s]+1)%2
        
        self.generate_network()

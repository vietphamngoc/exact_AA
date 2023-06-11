# import numpy as np
# import os

# import code.circuits.qaa as qaa
# import code.utilities.utility as util

# from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
# from qiskit.providers.aer import QasmSimulator

# from code.circuits.oracle import Oracle
# from code.circuits.tnn import TNN
# from code.update_strat.updates import update_delta

# n = 4

# os.chdir(f"{os.getcwd()}/results/delta_3")
# print(os.getcwd())
# simulator = QasmSimulator()

# fcts = util.get_functions(n, 16, "delta_3")
# print(fcts[8])

# ora = Oracle(n, fcts[8])
# tun_net = TNN(n)
# tun_net.gates["0110"] = 1
# # tun_net.gates["1001"] = 1
# tun_net.generate_network()

# diffusion = qaa.get_diffusion_operator(ora, tun_net, 2)

# qr = QuantumRegister(n, 'x')
# qar = QuantumRegister(2, 'a')
# cr = ClassicalRegister(n)
# car = ClassicalRegister(2)
# qc = QuantumCircuit(qr, qar, cr, car)

# qc.append(ora.gate, range(n+1))
# qc.append(tun_net.network, range(n+1))
# qc.cry(np.pi, qar[0], qar[1])

# for m in range(0):
#     qc.append(diffusion, range(n+2))

# qc.measure(qr, cr)
# qc.measure(qar, car)

# compiled_circuit = transpile(qc, simulator)
# job = simulator.run(compiled_circuit, shots=64)
# result = job.result()
# counts = result.get_counts(compiled_circuit)

# measurements = {'errors':[], 'corrects':[]}

# for sample in counts:
#     input = sample[3:][::-1]
#     if sample[0:2] == "11":
#         measurements["errors"].append(input)

#     if sample[0:2] == "00":
#         measurements["corrects"].append(input)

# update_delta(n, 3, measurements)

from code.stats.get_stats import parallel_stats

parallel_stats(5, 16, 20, "delta_4")




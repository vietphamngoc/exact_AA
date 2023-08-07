import numpy as np

import code.circuits.qaa as qaa

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.providers.aer import QasmSimulator
from qiskit.quantum_info import DensityMatrix

from scipy.special import binom

from code.circuits.oracle import Oracle
from code.circuits.tnn import TNN
from code.update_strat.updates import update_delta, update_junta


simulator = QasmSimulator()


def exact_learn(ora: Oracle, tun_net: TNN, concept: str, k_0: int=2, step: int=2, cut: int=100):
    """
    Function performing the exact learning.

    Arguments:
        - ora: Oracle, the query oracle for the target concept
        - tun_net: TNN, the network to be tuned
        - cut: int (default=100), the cut off threshold
        - step: int (default=1), the increment step size

    Returns:
        - The number of updates needed to learn exactly the target function
    """
    if step < 1:
        raise ValueError("step must be greater or equal to 1")

    n = ora.dim

    theta_min = np.arcsin(np.sin(np.pi/(4*k_0+2))*np.sqrt(1/2**n))
    k_max = int(np.round(0.5*((np.pi/(2*theta_min))-1)))

    # Setting the schedule for the number of oracle iterations
    if step == 1:
        schedule = range(k_0, k_max+1)
    else:
        schedule = [k_0]
        if k_0 == 0:
            power = 0
        else:
            power = int(np.ceil(np.log(k_0)/np.log(step)))

        k = int(np.round(step**power))
        while k < k_max:
            if k not in schedule:
                schedule.append(k)
            power += 1
            k = int(np.ceil(step**power))
        schedule.append(k_max)

    if concept[:6] == "junta_":
        l = int(concept.split("_")[1])

        num = 0
        for i in range(l+1):
            num += binom(n,i)
        angle = np.arcsin(np.sqrt(num/2**n))
        rounds = int(np.round(((np.pi/(2*angle))-1)/2))

    s = 1
    n_update = 0

    measurements = {}
    measurements['errors'] = []
    measurements['corrects'] = []
    measured = []

    # Stops when k = k_max and s = 0
    while s > 0:
        s = 0
        for k in schedule:
            if concept[:6] == "delta_":
                l = int(concept.split("_")[1])
                N_k = np.round((2**l)*(np.sin(np.pi/(4*k+6))/np.sin(np.pi/(4*k_0+2)))**2)
            else:
                N_k = np.round((2**n)*(np.sin(np.pi/(4*k+6))/np.sin(np.pi/(4*k_0+2)))**2)

            if N_k >=4:
                N = int(np.ceil(N_k*np.log(N_k)))
            else:
                N = 5

            if concept[:6] == "junta_":
                N = 2**l

            # diffusion = qaa.get_diffusion_operator(ora, tun_net, k_0)

            # Creating the circuit
            qr = QuantumRegister(n, 'x')
            qar = QuantumRegister(2, 'a')
            cr = ClassicalRegister(n)
            car = ClassicalRegister(2)
            qc = QuantumCircuit(qr, qar, cr, car)

            # Applying the oracle, the network and scaling down
            qc.append(ora.gate, range(n+1))

            if concept[:6] == "junta_":
                original_density = DensityMatrix(qc)
                diffusion_k = qaa.get_diffusion_k(original_density, n, k)

                for r in range(rounds):
                    qc.append(diffusion_k,range(n+2))

            density = DensityMatrix(qc)

            qc.append(tun_net.network, range(n+1))
            qc.cry(np.pi/(2*k_0+1), qar[0], qar[1])

            diffusion = qaa.get_diffusion_from_density(density, tun_net, k_0)

            # Applying amplitude amplification
            for m in range(k):
                qc.append(diffusion, range(n+2))

            # Measuring
            qc.measure(qr, cr)
            qc.measure(qar, car)

            # Running the circuit
            compiled_circuit = transpile(qc, simulator)
            job = simulator.run(compiled_circuit, shots=N)
            result = job.result()
            counts = result.get_counts(compiled_circuit)

            # Getting the errors and corrects and counting the errors
            for sample in counts:
                input = sample[3:][::-1]
                if sample[1] == "1":
                    s += counts[sample]
                    if input not in measured:
                        measurements["errors"].append(input)
                        measured.append(input)
                if sample[1] == "0":
                    if input not in measured:
                        measurements["corrects"].append(input)
                        measured.append(input)
  
        if concept[:6] == "delta_":
            to_update = update_delta(n, measurements, tun_net)
        elif concept[:6] == "junta_":
            to_update = update_junta(n, l, measurements, tun_net)
        else:
            if "0"*n in measurements["errors"]:
                to_update = ["0"*n]
            else:
                to_update = measurements["errors"]

        # If s !=0: there are misclassified inputs to be corrected 
        if s != 0:
            tun_net.update_tnn(to_update)
            # print(f"network: {[k for k,v in tun_net.gates.items() if v==1]}\n")
            n_update += 1
            measurements['errors'] = []
            measurements['corrects'] = []
            measured = []

        if n_update==cut:
            return -1
    return n_update


def exact_learn_no_AA(ora: Oracle, tun_net: TNN, cut: int=100):
    """
    Function performing the exact learning.

    Arguments:
        - ora: Oracle, the query oracle for the target concept
        - tun_net: TNN, the network to be tuned
        - cut: int (default=100), the cut off threshold
        - step: int (default=1), the increment step size

    Returns:
        - The number of updates needed to learn exactly the target function
    """
    n = ora.dim
    N = int(np.round((2**n)*np.log(2**n)))
    s = 1
    n_update = 0

    measurements = {}
    measurements['errors'] = []
    measurements['corrects'] = []
    measured = []

    # Stops when k = k_max and s = 0
    while s > 0:
        s = 0

        tun_net.generate_network()

        # Creating the circuit
        qr = QuantumRegister(n, 'x')
        qar = QuantumRegister(1, 'a')
        cr = ClassicalRegister(n)
        car = ClassicalRegister(1)
        qc = QuantumCircuit(qr, qar, cr, car)

        # Applying the oracle and the network
        qc.append(ora.gate, range(n+1))
        qc.append(tun_net.network, range(n+1))

        # Measuring
        qc.measure(qr, cr)
        qc.measure(qar, car)

        # Running the circuit
        compiled_circuit = transpile(qc, simulator)
        job = simulator.run(compiled_circuit, shots=N)
        result = job.result()
        counts = result.get_counts(compiled_circuit)

        # Getting the errors and corrects and counting the errors
        for sample in counts:
            input = sample[2:][::-1]
            if sample[0] == "1":
                s += counts[sample]
                if input not in measured:
                    measurements["errors"].append(input)
                    measured.append(input)
            if sample[0] == "0":
                if input not in measured:
                    measurements["corrects"].append(input)
                    measured.append(input)

        # If s !=0: there are misclassified inputs to be corrected 
        if s != 0:
            tun_net.update_tnn(measurements["errors"])
            n_update += 1
            measurements['errors'] = []
            measurements['corrects'] = []
            measured = []

        if n_update==cut:
            return -1
    return n_update

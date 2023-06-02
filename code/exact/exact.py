import numpy as np

import code.utilities.utility as util
import code.circuits.qaa as qaa

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.providers.aer import QasmSimulator

from code.circuits.oracle import Oracle
from code.circuits.tnn import TNN


simulator = QasmSimulator()


def exact_learn(ora: Oracle, tun_net: TNN, k_0: int=0, step: int=1, cut: int=100):
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
            p = 0
        else:
            p = int(np.ceil(np.log(k_0)/np.log(step)))
        k = int(np.round(step**p))
        while k < k_max:
            if k not in schedule:
                schedule.append(k)
            p += 1
            k = int(np.ceil(step**p))
        schedule.append(k_max)

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
            N_k = np.round((2**n)*(np.sin(np.pi/(4*k+6))/np.sin(np.pi/(4*k_0+2)))**2)

            if N_k >=4:
                N = int(np.ceil(N_k*np.log(N_k)))
            else:
                N = 5

            tun_net.generate_network()

            diffusion = qaa.get_diffusion_operator(ora, tun_net, k_0)

            # Creating the circuit
            qr = QuantumRegister(n, 'x')
            qar = QuantumRegister(2, 'a')
            cr = ClassicalRegister(n)
            car = ClassicalRegister(2)
            qc = QuantumCircuit(qr, qar, cr, car)

            # Applying the oracle, the network and scaling down
            qc.append(ora.gate, range(n+1))
            qc.append(tun_net.network, range(n+1))
            qc.cry(np.pi/(2*k_0+1), qar[0], qar[1])

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
                if sample[0:2] == "11":
                    s += counts[sample]
                    if input not in measured:
                        measurements["errors"].append(input)
                        measured.append(input)
                if sample[0:2] == "00":
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

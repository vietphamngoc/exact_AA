import os
import pickle

import code.utilities.utility as util

from code.circuits.oracle import Oracle
from code.circuits.tnn import TNN
from code.exact.exact import exact_learn, exact_learn_no_AA
from code.stats.error_rate import get_error_rate


def run_stats(n: int, number: int, runs: int, AA: bool=True, k_0: int=0, step: int=1):
    print("Start")

    script_directory = os.path.dirname(__file__)
    os.chdir(script_directory)
    os.chdir("../..")
    directory = f"{os.getcwd()}/results"
    if not os.path.isdir(directory):
        os.makedirs(directory)
    os.chdir(directory)

    functions = util.get_functions(n, number)

    if AA:
        run_directory = f"{os.getcwd()}/runs/{n}/{k_0}_{step}"
    else:
        run_directory = f"{os.getcwd()}/runs/{n}/no_AA"

    if not os.path.exists(run_directory):
        os.makedirs(run_directory)

    for j in range(runs):
        print(f"Run {j+1}")

        error_file = f"{run_directory}/errors_{j+1}.txt"
        upd_file = f"{run_directory}/updates_{j+1}.txt"

        if not os.path.exists(error_file) or not os.path.exists(upd_file):
            errors = {}
            ns_update = {}

        else:
            with open(error_file, "rb") as f:
                errors = pickle.load(f)
            with open(upd_file, "rb") as f:
                ns_update = pickle.load(f)

        for i in range(len(functions)):
            if (i+1) % 5 == 0:
                print(f"{i+1}/{len(functions)}")
                with open(error_file, "wb") as f:
                    pickle.dump(errors, f)
                with open(upd_file, "wb") as f:
                    pickle.dump(ns_update, f)

            fct = functions[i]

            if fct not in errors or fct not in ns_update:
                ora = Oracle(n, fct)
                tun_net = TNN(n)

                if AA:
                    n_update = exact_learn(ora, tun_net, k_0=k_0, step=step)
                else:
                    n_update = exact_learn_no_AA(ora, tun_net, cut=50)

                ns_update[fct] = n_update


                err = get_error_rate(ora, tun_net)
                errors[fct] = err

        with open(error_file, "wb") as f:
            pickle.dump(errors, f)
        with open(upd_file, "wb") as f:
            pickle.dump(ns_update, f)

import os
import pickle

import code.utilities.utility as util

from joblib import Parallel, delayed

from code.circuits.oracle import Oracle
from code.circuits.tnn import TNN
from code.exact.exact import exact_learn, exact_learn_no_AA
from code.stats.error_rate import get_error_rate


def get_settings(n, number, concept, AA):
    script_directory = os.path.dirname(__file__)
    os.chdir(script_directory)
    os.chdir("../..")
    directory = f"{os.getcwd()}/results/{concept}"
    if not os.path.isdir(directory):
        os.makedirs(directory)
    os.chdir(directory)

    functions = util.get_functions(n, number, concept)

    if AA:
        run_directory = f"{os.getcwd()}/runs/{n}"
    else:
        run_directory = f"{os.getcwd()}/runs/{n}/no_AA"

    if not os.path.exists(run_directory):
        os.makedirs(run_directory)

    return functions, run_directory


def one_run(n, AA, concept, functions, run_directory, j):
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
            print(f"Run {j+1}: {i+1}/{len(functions)}")
            with open(error_file, "wb") as f:
                pickle.dump(errors, f)
            with open(upd_file, "wb") as f:
                pickle.dump(ns_update, f)

        fct = functions[i]

        if fct not in errors or fct not in ns_update:
            ora = Oracle(n, fct)
            tun_net = TNN(n)

            if AA:
                n_update = exact_learn(ora, tun_net, concept, 2, 2)
            else:
                n_update = exact_learn_no_AA(ora, tun_net, cut=50)

            ns_update[fct] = n_update


            err = get_error_rate(ora, tun_net)
            errors[fct] = err

    with open(error_file, "wb") as f:
        pickle.dump(errors, f)
    with open(upd_file, "wb") as f:
        pickle.dump(ns_update, f)


def run_stats(n: int, number: int, runs: int, concept: str, AA: bool=True):
    print("Start")
    functions, run_directory = get_settings(n, number, concept, AA)

    for j in range(runs):
        one_run(n, AA, concept, functions, run_directory, j)


def parallel_stats(n: int, number: int, runs: int, concept: str, AA: bool=True, n_jobs: int=4):
    print("Start")
    functions, run_directory = get_settings(n, number, concept, AA)

    Parallel(n_jobs=n_jobs)(delayed(one_run)(n, AA, concept, functions, run_directory, j) for j in range(runs))


    

        

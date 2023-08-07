import numpy as np
import pickle
import random
import os


def ones_to_str(ones: set, n: int)->str:
    """
    Function to transform the set of positions of '1's into the corresponding binary string.

    Arguments:
        - ones: set, the set of positions
        - n: int, the length of the resulting binary string

    Returns:
        The binary string of length n where the '1's are at the positions collected in ones
    """
    binary = ["0" for i in range(n)]
    for i in ones:
        binary[i] = "1"
    return "".join(binary)


def str_to_ones(string: str)->set:
    """
    Function to transform a binary string into a set collecting the positions of the '1's.

    Arguments:
        - string: str, the binary string

    Returns:
        The set collecting the positions of the '1's in string
    """
    ones = [i for i in range(len(string)) if string[i] == "1"]
    return set(ones)


def generate_functions(n: int, number: int):
    if number <= 0:
        raise ValueError("number must be > 0")
    functions = []
    while len(functions) < number:
        f = ""
        for i in range(2**n):
            f += str(random.randint(0, 1))
        if f not in functions:
            functions.append(f)
    return functions


def generate_delta_table(n, ctrls):
    table = []
    for i in range(2**n):
        binary = format(i, f"0{n}b")
        s = 0
        for ctrl in ctrls:
            p = 1
            for c in ctrl:
                if binary[c] == "0":
                    p = 0
                    break
            s += p
        table.append(str(s%2))
    return "".join(table)


def generate_delta_controls(n: int, k: int):
    if k < 1 or k >= n:
        raise ValueError("k should be 0 < k < n")
    cards = []
    rest = k
    while rest > 0:
        card = random.randint(1, rest)
        cards.append(card)
        rest -= card
    choices = list(range(n))  
    ctrls = []
    for card in cards:
        ctrl = []
        for _ in range(card):
            idx = random.randint(0, len(choices)-1)
            ctrl.append(choices[idx])
            choices.pop(idx)
        ctrls.append(ctrl)
    return ctrls


def generate_delta_functions(n: int, k: int, number: int):
    fcts = []
    while len(fcts) < number:
        ctrls = generate_delta_controls(n, k)
        table = generate_delta_table(n, ctrls)
        if table not in fcts:
            fcts.append(table)
    return fcts


def generate_junta(n: int, k:int):
    if k < 1 or k >= n:
        raise ValueError("k should be 0 < k < n")
    ctrls = []
    choices = list(range(n))
    sub_table = "0"
    table = ""

    while len(ctrls) < k:
        idx = random.randint(0, len(choices)-1)
        ctrls.append(choices[idx])
        choices.pop(idx)
    ctrls.sort()

    for _ in range(1,2**k):
        sub_table += str(random.randint(0,1))

    for i in range(2**n):
        binary = format(i, f"0{n}b")
        sub_binary = "".join([binary[b] for b in ctrls])
        equiv = int(sub_binary, 2)
        table += sub_table[equiv]
    return table


def generate_junta_functions(n: int, k: int, number: int):
    fcts = []
    while len(fcts) < number:
        table = generate_junta(n, k)
        if table not in fcts:
            fcts.append(table)
    return fcts


def get_functions(n: int, number: int, concept: str):
    """
    Function to save a set of target concepts in a file, if this file exists, retrieve the functions.

    Arguments:
        - n: int, the dimension of the input space
        - number: int (default=0), the number of functions in the set. If 0, then it is the whole class of concepts

    Returns:
        - A list containing the functions
    """
    if number > 2**(2**n) or number <= 0:
        raise ValueError(f"number should be 0 < number <= {2**(2**n)}")
    
    if concept != any and concept[:6] not in ["delta_", "junta_"]:
        raise ValueError("type must be either 'any' or of the form 'delta_k' or 'junta_k'")

    directory = f"{os.getcwd()}/functions"

    if not os.path.exists(directory):
        os.makedirs(directory)

    file = f"{directory}/functions_{n}_{number}.txt"

    if os.path.exists(file):
        with open(file, "rb") as f:
            functions = pickle.load(f)
    else:
        if concept == "any":
            functions = generate_functions(n, number)
        elif concept[:6] == "delta_":
            k = int(concept.split("_")[1])
            functions = generate_delta_functions(n, k, number)
        else:
            k = int(concept.split("_")[1])
            functions = generate_junta_functions(n, k, number)

        with open(file, "wb") as f:
            pickle.dump(functions, f)

    return functions





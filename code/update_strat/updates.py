import code.utilities.utility as util

from code.circuits.tnn import TNN


def update_delta(n: int, measurements: dict, tun_net: TNN):
    to_update = []
    compound = set()
    active = [k for k,v in tun_net.gates.items() if v==1]
    ordered_errors = [[] for _ in range(n)]

    for err in measurements['errors']:
        ones = util.str_to_ones(err)
        ordered_errors[len(ones)-1].append(ones)
    print(ordered_errors)

    for l in ordered_errors:
        for ones in l:
            if compound.intersection(ones) == set():
                to_update.append(ones)
                compound = compound.union(ones)
                for a_g in active:
                    a_ones = util.str_to_ones(a_g)
                    if (ones.issubset(a_ones)) and (a_ones not in to_update):
                        to_update.append(a_ones) 

    return([util.ones_to_str(g, n) for g in to_update])
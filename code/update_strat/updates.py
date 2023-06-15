import code.utilities.utility as util

from code.circuits.tnn import TNN


def add_remove(ones: set, to_update: list, active: list):
    to_update.append(ones)
    for a_g in active:
        if (ones.issubset(a_g)) and (a_g not in to_update):
            to_update.append(a_g) 


def update_delta(n: int, measurements: dict, tun_net: TNN):
    to_update = []
    compound = set()
    active = [util.str_to_ones(k) for k,v in tun_net.gates.items() if v==1]
    ordered_errors = [[] for _ in range(n)]

    for err in measurements['errors']:
        ones = util.str_to_ones(err)
        ordered_errors[len(ones)-1].append(ones)

    for l in ordered_errors:
        for ones in l:
            if compound.intersection(ones) == set():
                add_remove(ones, to_update, active) 

    return([util.ones_to_str(g, n) for g in to_update])


def update_junta(n: int, k: int, measurements: dict, tun_net: TNN):
    active = [util.str_to_ones(o) for o,v in tun_net.gates.items() if v==1]

    if "0"*n in measurements['errors']:
        to_update = [set()]+active

    else:
        to_update = []
        ordered_errors = [[] for _ in range(n+1)]

        for err in measurements['errors']:
            ones = util.str_to_ones(err)
            ordered_errors[len(ones)].append(ones)

        for i in range(k+1):
            for ones in ordered_errors[i]:
                add_remove(ones, to_update, active)

        for i in range(k+1, n+1):
            for ones in ordered_errors[i]:
                subset = False
                for upd in to_update:
                    if upd.issubset(ones):
                        subset = True
                        break
                if not subset:
                    add_remove(ones, to_update, active) 

    return [util.ones_to_str(o, n) for o in to_update]
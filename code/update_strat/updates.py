import code.utilities.utility as util

from code.circuits.tnn import TNN


def add_remove(ones: set, to_update: list, active: list, threshold: int):
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
    # print(measurements)
    active = [util.str_to_ones(o) for o,v in tun_net.gates.items() if v==1]
    # print(f"active: {active}")
    to_update = []
    ordered_errors = [[] for _ in range(n+1)]
    ordered_corrects = [[] for _ in range(n+1)]


    for err in measurements['errors']:
        ones = util.str_to_ones(err)
        ordered_errors[len(ones)].append(ones)

    for cor in measurements['corrects']:
        ones = util.str_to_ones(cor)
        ordered_corrects[len(ones)].append(ones)

    # for i in range(k+1):
    #     for ones in ordered_errors[i]:
    #         add_remove(ones, to_update, active)
    # print(f"upd1: {to_update}")
    for i in range(n+1):
        for ones in ordered_errors[i]:
            filter = 0
            for upd in to_update:
                if upd.issubset(ones):
                    filter += 1
            if filter%2 == 0:
                add_remove(ones, to_update, active, k) 
        
        for ones in ordered_corrects[i]:
            filter = 0
            for upd in to_update:
                if upd.issubset(ones):
                    filter += 1
            if filter%2 == 1:
                # print(filter)
                add_remove(ones, to_update, active, k) 
    # print(f"upd: {to_update}")
    return [util.ones_to_str(o, n) for o in to_update]
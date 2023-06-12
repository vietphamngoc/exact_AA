import code.utilities.utility as util


def update_delta(n: int, k: int, measurements: dict):
    to_update = []
    ordered_errors = [[] for _ in range(n)]
    ordered_corrects = [[] for _ in range(n)]
    count = 0
    for err in measurements['errors']:
        ones = util.str_to_ones(err)
        ordered_errors[len(ones)-1].append(ones)
    print(ordered_errors)
    for cor in measurements['corrects']:
        if cor != "0"*n:
            ones = util.str_to_ones(cor)
            ordered_corrects[len(ones)-1].append(ones)
    print(ordered_corrects)

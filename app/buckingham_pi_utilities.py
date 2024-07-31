names_of_dimensions = (
    'luminous_intensity',
    'time',
    'electric_current',
    'temperature',
    'length',
    'mass',
    'amount_of_substance',
)


def find_matching_parenthesis(string, index, delimiters=None):
    depth = 0
    if delimiters is None:
        delimiters = ('(', ')')
    for k in range(index, len(string)):
        if string[k] == delimiters[0]:
            depth += 1
            continue
        if string[k] == delimiters[1]:
            depth += -1
            if depth == 0:
                return k
    return -1

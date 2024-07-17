names_of_prefixes_units_and_dimensions = (
    'quetta', 'ronna', 'yotta', 'zetta',
    'hecto', 'centi', 'milli', 'micro',
    'femto', 'zepto', 'yocto', 'peta',
    'tera', 'giga', 'mega', 'kilo', 
    'deka', 'deci', 'nano', 'pico',
    'atto', 'ronto', 'quecto', 'exa',
    'candela', 'second', 'ampere', 'kelvin',
    'metre', 'gram', 'mole', 'luminous_intensity',
    'time', 'electric_current', 'temperature', 'length',
    'mass', 'amount_of_substance', 'astronomicalunit', 'atomicmassunit',
    'nauticalmile', 'electronvolt', 'angleminute', 'anglesecond',
    'steradian', 'metricton', 'roentgen', 'angstrom',
    'hectare', 'radian', 'minute', 'degree',
    'curie', 'liter', 'neper', 'knot',
    'barn', 'hour', 'day', 'are',
    'bar', 'rad', 'rem', 'bel',
    'fluid ounce', 'gallon', 'quart', 'ounce',
    'pound', 'stone', 'inch', 'foot',
    'yard', 'mile', 'gill', 'pint'
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

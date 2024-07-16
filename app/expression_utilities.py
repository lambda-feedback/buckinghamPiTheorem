from sympy.parsing.sympy_parser import parse_expr, split_symbols_custom, _token_splittable
from sympy.parsing.sympy_parser import T as parser_transformations
from sympy import Symbol, I, E

elementary_functions_names = [
    ('sin', []), ('sinc', []), ('csc', ['cosec']), ('cos', []), ('sec', []), ('tan', []), ('cot', ['cotan']),
    ('asin', ['arcsin']), ('acsc', ['arccsc', 'arccosec', 'acosec']), ('acos', ['arccos']), ('asec', ['arcsec']),
    ('atan', ['arctan']), ('acot', ['arccot', 'arccotan', 'acotan']), ('atan2', ['arctan2']),
    ('sinh', []), ('cosh', []), ('tanh', []), ('csch', ['cosech']), ('sech', []),
    ('asinh', ['arcsinh']), ('acosh', ['arccosh']), ('atanh', ['arctanh']),
    ('acsch', ['arccsch', 'arccosech']), ('asech', ['arcsech']),
    ('exp', ['Exp']), ('E', ['e']), ('log', []),
    ('sqrt', []), ('sign', []), ('Abs', ['abs']), ('Max', ['max']), ('Min', ['min']), ('arg', []), ('ceiling', ['ceil']), ('floor', []),
    # Below this line should probably not be collected with elementary functions. Some like 'common operations' would be a better name
    ('summation', ['sum', 'Sum']), ('Derivative', ['diff']),
]
for data in elementary_functions_names:
    upper_case_alternatives = [data[0].upper()]
    for alternative in data[1]:
        if alternative.upper() not in upper_case_alternatives:
            upper_case_alternatives.append(alternative.upper())
    data[1].extend(upper_case_alternatives)

greek_letters = [
    "Alpha", "alpha", "Beta", "beta", "Gamma", "gamma", "Delta", "delta", "Epsilon", "epsilon", "Zeta", "zeta",
    "Eta", "eta", "Theta", "theta", "Iota", "iota", "Kappa", "kappa", "Lambda",  # "lambda" removed to avoid collision with reserved keyword in python
    "Mu", "mu", "Nu", "nu",
    "Xi", "xi", "Omicron", "omicron", "Pi", "pi", "Rho", "rho", "Sigma", "sigma", "Tau", "tau", "Upsilon", "upsilon",
    "Phi", "phi", "Chi", "chi", "Psi", "psi", "Omega", "omega"
]
special_symbols_names = [(x, []) for x in greek_letters]
elementary_functions_names += special_symbols_names
elementary_functions_names.sort(key=lambda x: -len(x))


# -------- String Manipulation Utilities
def preprocess_expression(exprs, params):
    '''
    Input:
        exprs  : a string or a list of strings
        params : Evaluation function parameter dictionary
    Output:
        List of strings where alternatives for input symbols have been replaced with
        their corresponsing input symbol code.
    Remark:
        Alternatives are sorted before substitution so that longer alternatives takes precedence.
    '''
    if isinstance(exprs, str):
        exprs = [exprs]

    substitutions = []

    if "symbols" in params.keys():
        input_symbols = params["symbols"]
        input_symbols_to_remove = []
        aliases_to_remove = []
        for (code, symbol_data) in input_symbols.items():
            if len(code) == 0:
                input_symbols_to_remove += [code]
            else:
                if len(code.strip()) == 0:
                    input_symbols_to_remove += [code]
                else:
                    aliases = symbol_data["aliases"]
                    for i in range(0, len(aliases)):
                        if len(aliases[i]) > 0:
                            aliases[i].strip()
                        if len(aliases[i]) == 0:
                            aliases_to_remove += [(code, i)]
        for (code, i) in aliases_to_remove:
            del input_symbols[code]["aliases"][i]
        for code in input_symbols_to_remove:
            del input_symbols[code]
        for (code, symbol_data) in input_symbols.items():
            substitutions.append((code, code))
            for alias in symbol_data["aliases"]:
                if len(alias) > 0:
                    substitutions.append((alias, code))

    # REMARK: This is to ensure capability with response areas that use the old formatting
    # for input_symbols. Should be removed when all response areas are updated.
    if "input_symbols" in params.keys():
        input_symbols = params["input_symbols"]
        input_symbols_to_remove = []
        alternatives_to_remove = []
        for k in range(0, len(input_symbols)):
            if len(input_symbols[k]) > 0:
                input_symbols[k][0].strip()
                if len(input_symbols[k][0]) == 0:
                    input_symbols_to_remove += [k]
            else:
                for i in range(0, len(input_symbols[k][1])):
                    if len(input_symbols[k][1][i]) > 0:
                        input_symbols[k][1][i].strip()
                    if len(input_symbols[k][1][i]) == 0:
                        alternatives_to_remove += [(k, i)]
        for (k, i) in alternatives_to_remove:
            del input_symbols[k][1][i]
        for k in input_symbols_to_remove:
            del input_symbols[k]
        for input_symbol in params["input_symbols"]:
            substitutions.append((input_symbol[0], input_symbol[0]))
            for alternative in input_symbol[1]:
                if len(alternative) > 0:
                    substitutions.append((alternative, input_symbol[0]))

    if len(substitutions) > 0:
        substitutions.sort(key=lambda x: -len(x[0]))
        for k in range(0, len(exprs)):
            exprs[k] = substitute(exprs[k], substitutions)

    return exprs


def substitute(string, substitutions):
    '''
    Input:
        string        (required) : a string or a list of strings
        substitutions (required) : a list with elements of the form (string,string)
                                   or ((string,list of strings),string)
    Output:
        A string that is the input string where any occurence of the left element
        of each pair in substitutions have been replaced with the corresponding right element.
        If the first element in the substitution is of the form (string,list of strings) then
        the substitution will only happen if the first element followed by one of the strings
        in the list in the second element.
    Remarks:
        Substitutions are made in the input order but if a substitutions left element is a
        substring of a preceding substitutions right element there will be no substitution.
        In most cases it is good practice to sort the substitutions by the length of the left
        element in descending order.
        Examples:
            substitute("abc bc c", [("abc","p"), ("bc","q"), ("c","r")])
            returns: "p q r"
            substitute("abc bc c", [("c","r"), ("bc","q"), ("abc","p")])
            returns: "abr br r"
            substitute("p bc c", [("p","abc"), ("bc","q"), ("c","r")])
            returns: "abc q c"
            substitute("p bc c", [("c","r"), ("bc","q"), ("p","abc")])
            returns: "abc br r"
    '''
    if isinstance(string, str):
        string = [string]

    # Perform substitutions
    new_string = []
    for part in string:
        if not isinstance(part, str):
            new_string.append(part)
        else:
            index = 0
            string_buffer = ""
            while index < len(part):
                matched_start = False
                for k, pair in enumerate(substitutions):
                    if isinstance(pair[0], tuple):
                        match = False
                        for look_ahead in pair[0][1]:
                            if part.startswith(pair[0][0]+look_ahead, index):
                                match = True
                                break
                        substitution_length = len(pair[0][0])
                    else:
                        match = part.startswith(pair[0], index)
                        substitution_length = len(pair[0])
                    if match:
                        matched_start = True
                        if len(string_buffer) > 0:
                            new_string.append(string_buffer)
                            string_buffer = ""
                        new_string.append(k)
                        index += substitution_length
                        break
                if not matched_start:
                    string_buffer += part[index]
                    index += 1
            if len(string_buffer) > 0:
                new_string.append(string_buffer)

    for k, elem in enumerate(new_string):
        if isinstance(elem, int):
            new_string[k] = substitutions[elem][1]

    return "".join(new_string)


# -------- (Sympy) Expression Parsing Utilities
def create_sympy_parsing_params(params, unsplittable_symbols=tuple()):
    '''
    Input:
        params               : evaluation function parameter dictionary
        unsplittable_symbols : list of strings that will not be split when parsing
                               even if implicit multiplication is used.
    Output:
        parsing_params: A dictionary that contains necessary info for the
                        parse_expression function.
    '''

    if "symbols" in params.keys():
        to_keep = []
        for symbol in params["symbols"].keys():
            if len(symbol) > 1:
                to_keep.append(symbol)
        unsplittable_symbols += tuple(to_keep)

    if "input_symbols" in params.keys():
        to_keep = []
        for symbol in [x[0] for x in params["input_symbols"]]:
            if len(symbol) > 1:
                to_keep.append(symbol)
        unsplittable_symbols += tuple(to_keep)

    if params.get("specialFunctions", False) is True:
        from sympy import beta, gamma, zeta
    else:
        beta = Symbol("beta")
        gamma = Symbol("gamma")
        zeta = Symbol("zeta")
    if params.get("complexNumbers", False) is True:
        symbol_I = I
    else:
        symbol_I = Symbol("I")
    if params.get("elementary_functions", False) is True:
        symbol_E = E
    else:
        symbol_E = Symbol("E")
    e = symbol_E
    N = Symbol("N")
    abstract_O = Symbol("O")
    Q = Symbol("Q")
    S = Symbol("S")
    symbol_dict = {
        "beta": beta,
        "gamma": gamma,
        "zeta": zeta,
        "I": symbol_I,
        "N": N,
        "O": abstract_O,
        "Q": Q,
        "S": S,
        "E": symbol_E,
        "e": e
    }

    for symbol in unsplittable_symbols:
        symbol_dict.update({symbol: Symbol(symbol)})

    strict_syntax = params.get("strict_syntax", True)

    parsing_params = {"unsplittable_symbols": unsplittable_symbols, "strict_syntax": strict_syntax, "symbol_dict": symbol_dict, "extra_transformations": tuple(), "elementary_functions": params.get("elementary_functions", False)}

    return parsing_params


def parse_expression(expr, parsing_params):
    '''
    Input:
        expr           : string to be parsed into a sympy expression
        parsing_params : dictionary that contains parsing parameters
    Output:
        sympy expression created by parsing expr configured according
        to the parameters in parsing_params
    '''

    strict_syntax = parsing_params.get("strict_syntax", False)
    extra_transformations = parsing_params.get("extra_transformations", ())
    unsplittable_symbols = parsing_params.get("unsplittable_symbols", ())
    symbol_dict = parsing_params.get("symbol_dict", {})
    separate_unsplittable_symbols = [(x, " "+x+" ") for x in unsplittable_symbols]
    if parsing_params["elementary_functions"] is True:
        alias_substitutions = []
        for (name, alias) in elementary_functions_names:
            alias_substitutions += [(name, name)] + [(x, name) for x in alias]
        alias_substitutions.sort(key=lambda x: -len(x[0]))
        expr = substitute(expr, alias_substitutions)
        separate_unsplittable_symbols = [(x[0], " "+x[0]) for x in elementary_functions_names] + separate_unsplittable_symbols
        separate_unsplittable_symbols.sort(key=lambda x: -len(x[0]))
    expr = substitute(expr, separate_unsplittable_symbols)
    can_split = lambda x: False if x in unsplittable_symbols else _token_splittable(x)
    if strict_syntax:
        transformations = parser_transformations[0:4]+extra_transformations
    else:
        transformations = parser_transformations[0:4, 6]+extra_transformations+(split_symbols_custom(can_split),)+parser_transformations[8]
    parsed_expr = parse_expr(expr, transformations=transformations, local_dict=symbol_dict)
    return parsed_expr

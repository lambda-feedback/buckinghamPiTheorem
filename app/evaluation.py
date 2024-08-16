from typing import Any, TypedDict
from sympy import latex, Matrix, Integer, Add, posify, prod

from .buckingham_pi_utilities import names_of_dimensions, find_matching_parenthesis
from .expression_utilities import preprocess_expression, parse_expression, create_sympy_parsing_params
from .preview import preview_function


class Params(TypedDict):
    pass


class Result(TypedDict):
    is_correct: bool
    feedback: str


internal_feedback_responses = {
    "NO_RESPONSE": "No response submitted.",
    "NO_ANSWER": "No answer was given.",
    "QUANTITIES_NOT_WRITTEN_CORRECTLY": "List of quantities not written correctly.",
}

default_parsing_feedback_messages = {
    "PARSE_ERROR_WARNING": lambda x: f"`{x}` could not be parsed as a valid mathematical expression. Ensure that correct notation is used, that the expression is unambiguous and that all parentheses are closed.",
    "STRICT_SYNTAX_EXPONENTIATION": "Note that `^` cannot be used to denote exponentiation, use `**` instead.",
}


def feedback_not_dimensionless(groups):
    groups = list(groups)
    if len(groups) == 1:
        return f"The group {convert_to_latex(groups[0])} is not dimensionless."
    else:
        return "The groups "+", ".join([convert_to_latex(g) for g in groups[0:-1]])+" and "+convert_to_latex(groups[-1])+" are not dimensionless."


def convert_to_latex(expr):
    if isinstance(expr, str):
        return expr
    else:
        return "$"+latex(expr)+"$"


default_buckingham_pi_feedback_messages = {
    "VALID_CANDIDATE_SET": "",
    "NOT_DIMENSIONLESS": feedback_not_dimensionless,
    "MORE_GROUPS_THAN_REFERENCE_SET": "Response has more groups than necessary.",
    "CANDIDATE_GROUPS_NOT_INDEPENDENT": lambda r, n: f"Groups in response are not independent. It has {r} independent group(s) and contains {n} groups.",
    "TOO_FEW_INDEPENDENT_GROUPS": lambda name, r, n: f"{name} contains too few independent groups. It has {r} independent group(s) and needs at least {n} independent groups.",
    "UNKNOWN_SYMBOL": lambda symbols: "Unknown symbol(s): "+", ".join([convert_to_latex(s) for s in symbols])+".",
    "SUM_WITH_INDEPENDENT_TERMS": lambda s: f"Sum in {convert_to_latex(s)} contains more independent terms that there are groups in total. Group expressions should ideally be written as a comma-separated list where each item is an entry of the form "+r"$q_1^{c_1} q_2^{c_2}\ldots q_n^\{c_n\}$."
}

line_break = "<br>"


def get_exponent_matrix(expressions, symbols):
    exponents_list = []
    for expression in expressions:
        exponents = []
        for symbol in symbols:
            exponent = expression.as_coeff_exponent(symbol)[1]
            if exponent == 0:
                exponent = -expression.subs(symbol, 1/symbol).as_coeff_exponent(symbol)[1]
            exponents.append(exponent)
        exponents_list.append(exponents)
    return Matrix(exponents_list)


def create_power_product(exponents, symbols):
    return prod([s**i for (s, i) in zip(symbols, exponents)])


def determine_validity(reference_set, reference_symbols, reference_original_number_of_groups, candidate_set, candidate_symbols, candidate_original_number_of_groups, feedback_messages):
    '''
    Analyses if the given candidate set satisfies the Buckingham Pi theorem assuming that the given reference set does.
    '''
    symbols = set(reference_symbols).union(set(candidate_symbols))
    R = get_exponent_matrix(reference_set, symbols)
    C = get_exponent_matrix(candidate_set, symbols)
    D = R.col_join(C)
    feedback = []
    more_groups_than_reference_set = reference_original_number_of_groups < candidate_original_number_of_groups
    candidate_groups_independent = C.rank() == candidate_original_number_of_groups
    rank_R_equal_to_rank_D = R.rank() == D.rank()
    rank_C_equal_to_rank_D = C.rank() == D.rank()
    if candidate_symbols.issubset(reference_symbols):
        valid = not more_groups_than_reference_set
        if more_groups_than_reference_set:
            feedback.append(feedback_messages["MORE_GROUPS_THAN_REFERENCE_SET"])
        valid = valid and candidate_groups_independent
        if not candidate_groups_independent:
            feedback.append(feedback_messages["CANDIDATE_GROUPS_NOT_INDEPENDENT"](C.rank(), len(candidate_set)))
        if rank_R_equal_to_rank_D:
            if rank_C_equal_to_rank_D:
                feedback.append(feedback_messages["VALID_CANDIDATE_SET"])
            else:
                valid = False
                feedback.append(feedback_messages["TOO_FEW_INDEPENDENT_GROUPS"]("Response", C.rank(), D.rank()))
        else:
            valid = False
            if len(candidate_set) == 1:
                dimensionless_groups = candidate_set
            else:
                dimensionless_groups = set()
                for i in range(len(candidate_set)):
                    exponents = C.row(i)
                    Di = R.col_join(exponents)
                    if R.rank() != Di.rank():
                        dimensionless_groups.add(create_power_product(exponents, symbols))
            feedback.append(feedback_messages["NOT_DIMENSIONLESS"](dimensionless_groups))
    else:
        feedback.append(feedback_messages["UNKNOWN_SYMBOL"](candidate_symbols.difference(reference_symbols)))
        valid = False
    feedback = [elem.strip() for elem in feedback if len(elem.strip()) > 0]
    return valid, line_break.join(feedback)


def evaluation_function(response: Any, answer: Any, params: Params) -> Result:
    """
    Function used to evaluate a student response.
    ---
    The handler function passes three arguments to evaluation_function():

    - `response` which are the answers provided by the student.
    - `answer` which are the correct answers to compare against.
    - `params` which are any extra parameters that may be useful,
        e.g., error tolerances.

    The output of this function is what is returned as the API response
    and therefore must be JSON-encodable. It must also conform to the
    response schema.

    Any standard python library may be used, as well as any package
    available on pip (provided it is added to requirements.txt).

    The way you wish to structure you code (all in this function, or
    split into many) is entirely up to you. All that matters are the
    return types and that evaluation_function() is the main function used
    to output the evaluation response.
    """

    """
    Function that provides some basic dimensional analysis functionality.
    """

    # Utility function that wraps a string in a function that takes an
    # arbitrary number of arguments
    def wrap_feedback_function(output):
        def wrapped_function(*args):
            return output
        return wrapped_function

    # Take custom feedback string given by task author and
    # replace the corresponding entries in the feedback response
    # dictionaries, wrapping pure stings in a function that takes
    # an arbitrary number of arguments when necessary
    # NOTE: Changing the entries in this way is known to cause
    # undesired behaviour when used in the lambda-feedback web
    # client, it will be fixed after the discussion with other
    # members of the development team
    custom_feedback = params.get("custom_feedback", None)
    feedback_messages = {**default_parsing_feedback_messages, **default_buckingham_pi_feedback_messages}
    if custom_feedback is not None:
        for key in custom_feedback.keys():
            if key in feedback_messages.keys():
                if isinstance(feedback_messages[key], str):
                    feedback_messages[key] = custom_feedback[key]
                elif callable(feedback_messages[key]):
                    feedback_messages[key] = wrap_feedback_function(custom_feedback[key])
                else:
                    raise Exception("Cannot handle given costum feedback for "+key)

    # Uses the preview function to translate latex input to  a
    # sympy compatible representation
    if params.get("is_latex", False):
        response = preview_function(response, params)["preview"]["sympy"]

    # Set default parameters if not already set
    parameters = {"comparison": "expression", "strict_syntax": True}
    parameters.update(params)

    # Raise exceptions when answer or response is missing from input
    if not isinstance(answer, str):
        raise Exception("No answer was given.")
    if not isinstance(response, str):
        return Result(is_correct=False, feedback="No response submitted.")

    answer = answer.strip()
    response = response.strip()
    if len(answer) == 0:
        raise Exception(feedback=internal_feedback_responses["NO_ANSWER"])
    if len(response) == 0:
        return Result(is_correct=False, feedback=internal_feedback_responses["NO_RESPONSE"])

    # Preprocess answer and response to prepare for parsing by sympy
    unsplittable_symbols = names_of_dimensions
    answer, response = preprocess_expression([answer, response], parameters)
    parsing_params = create_sympy_parsing_params(parameters, unsplittable_symbols=unsplittable_symbols)

    # Remark on syntax if necessary
    remark = ""
    if parameters["strict_syntax"]:
        if "^" in response:
            remark += feedback_messages["STRICT_SYNTAX_EXPONENTIATION"]
        if "^" in answer:
            raise Exception(feedback_messages["STRICT_SYNTAX_EXPONENTIATION"])
    remark = "" if len(remark) == 0 else line_break+remark

    # Parse expressions for groups in response and answer
    response_strings = response.split(',')
    response_number_of_groups = len(response_strings)
    response_original_number_of_groups = len(response_strings)
    response_groups = []
    for res in response_strings:
        try:
            expr = parse_expression(res, parsing_params).simplify()
            expr = expr.expand(power_base=True, force=True)
        except Exception:
            return Result(
                is_correct=False,
                feedback=feedback_messages["PARSE_ERROR_WARNING"](response)+remark
            )
        if isinstance(expr, Add):
            response_groups += list(expr.args)
            response_number_of_groups += len(list(expr.args))
        else:
            response_groups.append(expr)
            response_number_of_groups += 1
    response_latex = [latex(expr) for expr in response_groups]

    result = Result(response_latex=", ".join(response_latex))

    if answer == "-":
        answer_strings = []
    else:
        answer_strings = answer.split(',')
    answer_groups = []
    answer_number_of_groups = 0
    answer_original_number_of_groups = 0
    for ans in answer_strings:
        try:
            expr = parse_expression(ans, parsing_params).simplify()
            expr = expr.expand(power_base=True, force=True)
        except Exception as e:
            raise Exception(feedback_messages["PARSE_ERROR_WARNING"]("The answer")) from e
        if isinstance(expr, Add):
            answer_groups += list(expr.args)
            answer_number_of_groups += len(list(expr.args))
        else:
            answer_groups.append(expr)
            answer_number_of_groups += 1
        answer_original_number_of_groups += 1

    # Find what different symbols for quantities there are
    if len(parameters.get("quantities", "").strip()) > 0:
        quantities_strings = parameters["quantities"]
        quantities = []
        index = quantities_strings.find("(")
        while index > -1:
            index_match = find_matching_parenthesis(quantities_strings, index)
            try:
                quantity_strings = eval(quantities_strings[index+1:index_match])
                quantity = tuple(map(lambda x: parse_expression(x, parsing_params), quantity_strings))
                quantities.append(quantity)
            except Exception:
                raise Exception(internal_feedback_responses["QUANTITIES_NOT_WRITTEN_CORRECTLY"])
            index = quantities_strings.find('(', index_match+1)
        response_symbols = list(map(lambda x: x[0], quantities))
        answer_symbols = response_symbols

        # Check how many dimensionless groups are needed
        dimension_symbols = set()
        for quantity in quantities:
            dimension_symbols = dimension_symbols.union(quantity[1].free_symbols)
        quantity_matrix = get_exponent_matrix([q[1] for q in quantities], dimension_symbols)
        number_of_groups = len(quantities)-quantity_matrix.rank()

        # If answer groups are not given, generate a valid set of groups to use as answer
        if answer_groups == []:
            # Compute answer groups from defined quantities
            nullspace_basis = quantity_matrix.T.nullspace()
            for basis_vector in nullspace_basis:
                multiplier = 1
                for i in range(0, basis_vector.rows):
                    if not isinstance(basis_vector[i, 0], Integer):
                        multiplier *= 1/basis_vector[i, 0]
                if multiplier != 1:
                    for i in range(0, basis_vector.rows):
                        basis_vector[i, 0] = round(basis_vector[i, 0]*multiplier)
            answer_groups = [1]*number_of_groups
            for i in range(0, len(answer_groups)):
                for j in range(0, len(quantities)):
                    answer_groups[i] *= quantities[j][0]**nullspace_basis[i][j]

        if answer == "-":
            answer_number_of_groups = number_of_groups
            answer_original_number_of_groups = number_of_groups

        # Analyse dimensions of answers and responses
        answer_dimensions = []
        for group in answer_groups:
            dimension = group
            for quantity in quantities:
                dimension = dimension.subs(quantity[0], quantity[1])
            answer_dimensions.append(posify(dimension)[0].simplify())

        # Check that answers are dimensionless
        for k, dimension in enumerate(answer_dimensions):
            if not dimension.is_constant():
                raise Exception(feedback_messages["NOT_DIMENSIONLESS"](answer_groups[k]))

        # Check that there is a sufficient number of independent groups in the answer
        answer_matrix = get_exponent_matrix(answer_groups, answer_symbols)
        if answer_matrix.rank() < number_of_groups:
            raise Exception(feedback_messages["TOO_FEW_INDEPENDENT_GROUPS"]("Answer", answer_matrix.rank(), number_of_groups))

    # Compare symbols used in answer and response
    response_symbols = set()
    for res in response_groups:
        response_symbols = response_symbols.union(res.free_symbols)
    answer_symbols = set()
    for ans in answer_groups:
        answer_symbols = answer_symbols.union(ans.free_symbols)
    if not response_symbols.issubset(answer_symbols):
        result["is_correct"] = False
        result["feedback"] = feedback_messages["UNKNOWN_SYMBOL"](response_symbols.difference(answer_symbols))
        return result
    answer_symbols = list(answer_symbols)

    # Checking if the given response is a valid set of groups
    reference_set = set(answer_groups)
    reference_symbols = set(answer_symbols)
    candidate_set = set(response_groups)
    candidate_symbols = set(response_symbols)
    valid, feedback_string = determine_validity(reference_set, reference_symbols, answer_original_number_of_groups, candidate_set, candidate_symbols, response_original_number_of_groups, feedback_messages)

    # Check the special case where one groups expression contains several power products
    answer_matrix = get_exponent_matrix(answer_groups, answer_symbols)
    if answer_matrix.rank() > answer_number_of_groups:
        raise Exception(feedback_messages["SUM_WITH_INDEPENDENT_TERMS"]("answer"))
    response_matrix = get_exponent_matrix(response_groups, answer_symbols)
    if response_matrix.rank() > response_original_number_of_groups:
        result["is_correct"] = False
        result["feedback"] = feedback_string+line_break+feedback_messages["SUM_WITH_INDEPENDENT_TERMS"]("response")+remark
        return result

    result["is_correct"] = valid
    result["feedback"] = feedback_string+remark
    return result

# buckinghamPiTheorem

Evaluates a candidate list of power products (e.g. `U*L/nu`, `p/rho/U^2`) for validity as a set of dimensionless quantities that satisfy the Buckingham Pi theorem.

For details on intended usage and examples see the user documentation:  [User documentation for `buckinghamPiTheorem`](https://lambda-feedback.github.io/user-documentation/user_eval_function_docs/buckinghamPiTheorem/#buckinghampitheorem)

The core part of the function is an algorithm that takes two sets of groups and determines if they generate the same nullspace. If one set of groups is valid and both groups generate the same nullspace then the second set of groups is also valid. It is assumed that the task author either supplies a valid set that can used to check the validity of response, or details on the dimensions of the quantities involved such that a valid set can be generated. For a more detailed discussion of the algorithm see: [Automated feedback on student attempts to produce a set of dimensionless power products from a list of quantities that describe a physical problem](https://doi.org/10.6084/m9.figshare.24850131), the evaluation implements the algorithm described there (see `determine_validity` in `evaluation.py`) together with some modifications (see below).

To extend the functionality of the evaluation function, the algorithm described in the preceding paragraph has been modified in two ways:
1. If no example set is supplied, but a list of quantities is, then an example of a valid set is constructed by constructing the dimensional matrix corresponding to the list of quantities and picking a set of independent groups that span its nullspace. This example set of groups is then used a reference answer.
2. If the response contains an expression in the form $a \cdot q_1^{c_1} \cdot q_2^{c_2} \cdots q_n^{c_n}$ where $q_1, q_2 \ldots q_n$ are quantities, $c_1, c_2 \ldots c_n$ rational numbers and $a$ a constant, with more than one term then the evaluation function extracts all the terms treats them as separate power products. For the response to be considered valid it is required that the original number of groups in the response (i.e. before term extraction) is the correct number of groups as given by the Buckingham Pi Theorem. For examples of this behaviour see the function description in the user documentation: [User documentation for `buckinghamPiTheorem`](https://lambda-feedback.github.io/user-documentation/user_eval_function_docs/buckinghamPiTheorem/#buckinghampitheorem)
The code for these modifications can be found in `evaluation_function` in `evaluation.py`.


## Inputs
All input parameters need to be supplied via the `params` input value to `evaluation_function` in `evaluation.py`.

There are four optional parameters that can be set: `custom_feedback`, `elementary_functions`, `quantities`, `strict_syntax`.

## `custom_feedback`

The dictionaries whose keys correspond to customisable feedback messages are listen in `feedback_responses_list` in `evaluation.py`.

The evaluation function also has a number of tags for messages that cannot be customised that are used for error messages. These tags and their corresponding message can be found in the `internal_feedback_responses` dictionary in `evaluation.py`.

## `elementary_functions`

Reserved elementary functions names and their alternatives are listed in `expression_utilities.py`.

### `quantities`

List of default dimension names can be found in `buckingham_pi_utilities.py`.

### `strict_syntax`

The default value for `strict_syntax` is set in `evaluation.py`.
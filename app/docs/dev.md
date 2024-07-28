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

Custom feedback can be set on a per-task basis. **Note:** Custom feedback only supports fixed strings, this means that for some situations the custom feedback cannot be as detailed as the default feedback.

The parameter must be set as a dictionary with keys from the feedback tags listed below. The value for each key can be any string.

### Tags for customisable feedback
- `PARSE_ERROR_WARNING` Response cannot be parsed as an expression or physical quantity.
- `PER_FOR_DIVISION` Warns about risk of ambiguity when using `per` instead `/` for division.
- `STRICT_SYNTAX_EXPONENTIATION` Warns that `^` cannot be used for exponentiation when `strict_syntax` is set to `true`.
- `VALID_CANDIDATE_SET` Message that is displayed when a response is found to be a valid set of groups. **Note:** setting this will not affect the Correct/Incorrect message, it will only add further text.
- `NOT_DIMENSIONLESS` Message displayed when at least one groups is not dimensionless.
- `MORE_GROUPS_THAN_REFERENCE_SET` Message displayed when the response contains more groups than necessary.
- `CANDIDATE_GROUPS_NOT_INDEPENDENT` Message displayed when the groups in the response are not independent.
- `TOO_FEW_INDEPENDENT_GROUPS` Message displayed when the response contains fewer groups than necessary.
- `UNKNOWN_SYMBOL` Message displayed when the response contains some undefined symbol.
- `SUM_WITH_INDEPENDENT_TERMS`  Message displayed when the response has too few groups but one (or more) of the groups is a sum with independent terms.

The evaluation function also has a number of tags for messages that cannot be customised that are used for error messages. These tags and their corresponding message can be found in the `internal_feedback_responses` dictionary in `evaluation.py`. The dictionaries whose keys correspond to customisable feedback messages are listen in `feedback_responses_list` in `evaluation.py`.

## `elementary_functions`

When using implicit multiplication function names with mulitple characters are sometimes split and not interpreted properly. Setting `elementary_functions` to true will reserve the function names listed below and prevent them from being split. If a name is said to have one or more alternatives this means that it will accept the alternative names but the reserved name is what will be shown in the preview.

`sin`, `sinc`, `csc` (alternative `cosec`), `cos`, `sec`, `tan`, `cot` (alternative `cotan`), `asin` (alternative `arcsin`), `acsc` (alternatives `arccsc`, `arccosec`), `acos` (alternative `arccos`), `asec` (alternative `arcsec`), `atan` (alternative `arctan`), `acot` (alternatives `arccot`, `arccotan`), `atan2` (alternative `arctan2`), `sinh`, `cosh`, `tanh`, `csch` (alternative `cosech`), `sech`, `asinh` (alternative `arcsinh`), `acosh` (alternative `arccosh`), `atanh` (alternative `arctanh`), `acsch` (alternatives `arccsch`, `arcosech`), `asech` (alternative `arcsech`), `exp` (alternative `Exp`), `E` (equivalent to `exp(1)`, alternative `e`), `log`, `sqrt`, `sign`, `Abs` (alternative `abs`), `Max` (alternative `max`), `Min` (alternative `min`), `arg`, `ceiling` (alternative `ceil`), `floor`

### `quantities`

String that lists all quantities that can be used in the answer and response.

Each quantity should be written in the form `('quantity name','(dimensions)')` and all pairs concatenated into a single string. See tables below for available default dimensions.

#### Table: Base SI units

Default dimensions correspond to the base quantities in Table 1 of the [NIST Guide to the SI, Chapter 4: The Two Classes of SI Units and the SI Prefixes](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-4-two-classes-si-units-and-si-prefixes)

| Dimension name      |
|---------------------|
| length              |
| mass                |
| time                |
| electriccurrent     |
| temperature         |
| amountofsubstance   |
| luminousintensity   |

List of default dimension names can be found in `buckingham_pi_utilities.py`.

### `strict_syntax`

If `strict_syntax` is set to true then the answer and response must have `*` or `/` between each part of the expressions and exponentiation must be done using `**`, e.g. `a*b/c**2` is accepted but `ab/c^2` is not.

If `strict_syntax` is set to false, then `*` can be omitted and `^` used instead of `**`, e.g. `a*b/c**2` and `ab/c^2` will be considered identical. In this case it is also recommended to list any multicharacter symbols expected to appear in the response as input symbols.

By default `strict_syntax` is set to true.
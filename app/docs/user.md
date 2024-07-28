# buckinghamPiTheorem

Evaluates a candidate list of power products (e.g. `U*L/nu`, `p/rho/U^2`) for validity as a set of dimensionless quantities that satisfy the Buckingham Pi theorem. Uses a modified  version of the algorithm described in [Automated feedback on student attempts to produce a set of dimensionless power products from a list of quantities that describe a physical problem](https://doi.org/10.6084/m9.figshare.24850131)

There are three different ways of supplying this function with the necessary information.
1. In `answer`, provide an example set of groups as a comma separated list. When used this way the function assumes that the given example is a valid set containing the minimum number of groups.
2. In the `quantities` parameter, supply a comma-separated list of the dimensions for each quantity and set `answer` to `-`. The function will then compute a list of sufficiently many independent dimensionless quantities and compare to the response.
3. Fill in the `answer` as per option **1** and `quantities` as per option **2**. The function will then confirm that the supplied `answer` is dimensionless and valid before comparing it to the response. If the supplied `answer` is not valid the function will return an error regardless of the response.

Note that in lists of groups the items should ideally be written as power products, i.e. in the form $q_1^{c_1} \cdot q_2^{c_2} \cdots q_n^{c_n}$ where $q_1, q_2 \ldots q_n$ are quantities and $c_1, c_2 \ldots c_n$ are integers. For example, consider a task where $\frac{U L}{\nu}, \frac{nu}{f L^2}$ is a valid set:
- The responses `U*L/nu, nu/(f*L^2)` and `U L nu^(-1), nu f^(-1) L^(-2)` are examples of responses written in the ideal format,
- The response `U^(0.33)*L^(0.33)/nu^(0.33), nu/(f*L^2)^(2/3)` is theoretically valid, but can cause unexpected behaviour during comparison with response, due to non-integer exponents,
- `sin(U*L/nu), log(nu/(f*L^2)^(2/3))` will not be accepted since the two expressions are not power products.

The function can also handle sums of power products multiplied by constants. If the total number of groups is less than required the set of groups is considered invalid, even if there is a sufficient number of terms with independent power products in the response.
For example, consider a task where $\frac{U L}{\nu}, \frac{nu}{f L^2}$ is a valid set:
- The response `U*L/nu+1, nu/(f*L^2)+U*L/nu` will be considered valid, since there are two groups in the response, and if each term is considered separately the result is three different power products `U*L/nu`, `1` and `nu/(f*L^2)`, and the two non-constant expressions, `U*L/nu` and `nu/(f*L^2)`, are independent,
- The response `U*L/nu+1, nu/(f*L^2)+U/(f*L)` will be considered valid, since there are two groups in the response, and if each term is considered separately the result is four expressions `U*L/nu`, `1`, `nu/(f*L^2)` and `U/(f*L)` but only two of them, `U*L/nu` and `nu/(f*L^2)`, are independent (since `U/(f*L)` is equal to `U*L/nu * nu/(f*L^2)`),
- The response `U*L/nu+nu/(f*L^2)` will not be considered valid because even though the terms considered separately gives enough independent dimensionless power products, the response has too few expressions. 

## Inputs
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

### `strict_syntax`

If `strict_syntax` is set to true then the answer and response must have `*` or `/` between each part of the expressions and exponentiation must be done using `**`, e.g. `a*b/c**2` is accepted but `ab/c^2` is not.

If `strict_syntax` is set to false, then `*` can be omitted and `^` used instead of `**`, e.g. `a*b/c**2` and `ab/c^2` will be considered identical. In this case it is also recommended to list any multicharacter symbols expected to appear in the response as input symbols.

By default `strict_syntax` is set to true.

## Examples

Implemented versions of these examples can be found in the module 'Examples: Evaluation Functions'.

### 1 Checking if a set of quantities match the Buckingham pi theorem

#### a)

In this example the task is: Given $U$, $L$ and $\nu$, suggest a dimensionless group.

For this problem we do not need to predefine any quantities and give exact dimensions. The algorithm assumes that all symbols in the answer (that are not numbers or predefined constants such as $\pi$) are quantities and that there are no other quantities that should appear in the answer.

**Note:** This means that the algorithm does not in any way check that the stated answer is dimensionless, that is left to the task author.

For this example an EXPRESSION response area is used with answer set to `U*L/nu`. It is not necessary to use this specific answer, any example of a correct dimensionless group should work.

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the parameter `strict_syntax` is set to false. Since `nu` is a multicharacter symbol it needs to be added as an input symbol.

#### b)

In this example the task is: Given $U$, $L$, $\nu$ and $f$, determine the necessary number of dimensionless groups and give one example of possible expressions for them.

This task is similar to example a) with two significant differences. First, adding $f$ means that there are now two groups required, and second the task will constructed by defining the quantities and let the function compute the rest on its own instead of supplying a reference example.

For this example an EXPRESSION response area is used with `quantities` set to `('U','(length/time)') ('L','(length)') ('nu','(length**2/time)') ('f','(1/time)')` and `answer` set to `-`.

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the parameter `strict_syntax` is set to false. Since `nu` is a multicharacter symbol it needs to be added as an input symbol.

#### c)

In this example the task is:
Suppose we are studying water waves that move under the influence of gravity. We suppose that the variables of interest are the acceleration in free fall $g$, the velocity of the wave $v$, the height of the wave $h$ and the wave length $\ell$. We also suppose that they are related by a dimensionally consistent equation $f(g,v,h,l) = 0$. Determine the minimum number of dimensionless $\pi$-variables needed to describe this problem according to the Buckingham pi-theorem and give one example of possible expressions for the dimensionless quantities.

For this problem two dimensionless groups are needed, see the worked solution for a terse solution that gives the general form of the dimensionless quantities.

For this example an EXPRESSION response area is used and the answer  `g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4` (this corresponds to $p_1 = 1$, $p_2 = 2$, $q_1 = 3$, $q_2 = 4$ in the worked solution shown in the examples module). The feedback was customised by setting the `custom_feedback` parameter too:
`"custom_feedback": {
    "VALID_CANDIDATE_SET": "Your list of power products satisfies the Buckingham Pi theorem.",
    "NOT_DIMENSIONLESS": "At least one power product is not dimensionless.",
    "MORE_GROUPS_THAN_REFERENCE_SET": "Response has more power products than necessary.",
    "CANDIDATE_GROUPS_NOT_INDEPENDENT": "Power products in response are not independent.",
    "TOO_FEW_INDEPENDENT_GROUPS": "Candidate set contains too few independent groups.",
    "UNKNOWN_SYMBOL": "One of the prower products contains an unkown symbol.",
    "SUM_WITH_INDEPENDENT_TERMS": "The candidate set contains an expression which contains more independent terms that there are groups in total. The candidate set should ideally only contain expressions written as power products."
}`

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the parameter `strict_syntax` is set to false.
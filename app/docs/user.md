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
- `STRICT_SYNTAX_EXPONENTIATION` Warns that `^` cannot be used for exponentiation when `strict_syntax` is set to `true`.
- `VALID_CANDIDATE_SET` Message that is displayed when a response is found to be a valid set of groups. **Note:** setting this will not affect the Correct/Incorrect message, it will only add further text.
- `NOT_DIMENSIONLESS` Message displayed when at least one groups is not dimensionless.
- `MORE_GROUPS_THAN_REFERENCE_SET` Message displayed when the response contains more groups than necessary.
- `CANDIDATE_GROUPS_NOT_INDEPENDENT` Message displayed when the groups in the response are not independent.
- `TOO_FEW_INDEPENDENT_GROUPS` Message displayed when the response contains fewer groups than necessary.
- `UNKNOWN_SYMBOL` Message displayed when the response contains some undefined symbol.
- `SUM_WITH_INDEPENDENT_TERMS`  Message displayed when the response has too few groups but one (or more) of the groups is a sum with independent terms.

## `custom_feedback_combinations`
Custom feedback can be set on a per-task basis. **Note:** Custom feedback only supports fixed strings, this means that for some situations the custom feedback cannot be as detailed as the default feedback.

The `custom_feedback` parameters overrides the feedback for individual tags, it is also possible to override the feedback produced by specific combinations of tags using the `custom_feedback_combinations`. 

The vald format for the parameter is given below. The `CASE_NAME` values must be dinstinct string, but will otherwise be ignored, the tags must come from those listed for the `custom_feedback` parameter.

```
"custom_feedback_combinations": {
    "CASE_NAME_1": [
        [
            "TAG_1_1",
            ...
            "TAG_1_m"
        ],
        "FEEDBACK STRING 1"
    ],
    ...
    "CASE_NAME_N": [
        [
            "TAG_N_1",
            ...
            "TAG_N_k"
        ],
        "FEEDBACK STRING N"
    ]
}
```

**Note:** If there are more than one combination of tags present in the result, the tag list with the most members take precedence, e.g. if the results has tags `A, B, C, D` and there is custom feedback set for `A,B,C` and `A,B` then custom feedback for `A,B,C` will be shown together with the default feedback for `D`.

### Default feedback messages

The default feedback messages, including non-customisable ones are listed below:

| Tag                                | Remark                          | Feedback message |
|------------------------------------|:--------------------------------|:-----------------|
| `NO_RESPONSE`                      |                                 | "No response submitted." |
| `NO_ANSWER"                        |                                 | "No answer was given." |
| `QUANTITIES_NOT_WRITTEN_CORRECTLY` |                                 | "List of quantities not written correctly." |
| `PARSE_ERROR_WARNING`              | With response expression $E$    | "$E$ could not be parsed as a valid mathematical expression. Ensure that correct notation is used, that the expression is unambiguous and that all parentheses are closed." |
| `STRICT_SYNTAX_EXPONENTIATION`     |                                 | "Note that `^` cannot be used to denote exponentiation, use `**` instead." |
| `VALID_CANDIDATE_SET`              | Feedback message is omitted since correctness of the results will be displayed instead | "" |
| `NOT_DIMENSIONLESS`                | For response with a single group $G$ | "The group $G$ is not dimensionless." |
| `NOT_DIMENSIONLESS`                | For response where group $G_1 \ldots G_k$ are not dimensionless | "The groups $G_1 \ldots G_k$ and $G_k$ are not dimensionless." |
| `MORE_GROUPS_THAN_REFERENCE_SET`   |                                 | "Response has more groups than necessary." |
| `CANDIDATE_GROUPS_NOT_INDEPENDENT` |                                 | "Groups in response are not independent. It has $r$ independent group(s) and contains $n$ groups." |
| `TOO_FEW_INDEPENDENT_GROUPS`       | With response expression $E$          | "$E$ contains too few independent groups. It has $r$ independent group(s) and needs at least $n$ independent groups." |
| `UNKNOWN_SYMBOL`                   | With unknown symbols $s_1 \ldots s_k$ | "Unknown symbol(s): $s_1 \ldots s_k$." |
| `SUM_WITH_INDEPENDENT_TERMS`       | With response expression $E$    | "Sum in $S$ contains more independent terms that there are groups in total. Group expressions should ideally be written as a comma-separated list where each item is an entry of the form $q_1^{c_1} q_2^{c_2}\ldots q_n^{c_n}$." |

## `elementary_functions`

When using implicit multiplication (i.e. when `strict_syntax` is set to true) function names with multiple characters are sometimes split and not interpreted properly, e.g. `sin(x)` might be interpreted as `s*i*n*(x)`. Setting `elementary_functions` to true will reserve the function names listed below and prevent them from being split. If a name is said to have one or more alternatives this means that it will accept the alternative names but the reserved name is what will be shown in the preview.

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

If `strict_syntax` is set to true then the answer and response must have `*` or `/` between each part of the expressions and exponentiation must be done using `**`.

For example: with `strict_syntax` set to false `a*b` and `ab` will be interpreted as equivalent, but with `strict_syntax` set to false `ab` will be interpreted as a single symbol instead of a multiplication. 

If `strict_syntax` is set to false, then `^` used instead of `**`, e.g. `c**2` and `c^2` will be considered equivalent. In this case it is also recommended to list any multi-character symbols expected to appear in the response as input symbols. If `strict_syntax` is set to true then `c^2` will give a warning that `^` will not be interpreted as exponentiation.

By default `strict_syntax` is set to true.

## Examples

Implemented versions of these examples can be found in the module 'Examples: Evaluation Functions'.

### 1) Example where a valid set have one group

In this example the task is: Given $U$, $L$ and $\nu$, suggest a dimensionless group.

For this problem we do not need to predefine any quantities and give exact dimensions. The algorithm assumes that all symbols in the answer (that are not numbers or predefined constants such as $\pi$) are quantities and that there are no other quantities that should appear in the answer.

**Note:** This means that the algorithm does not in any way check that the stated answer is dimensionless, that is left to the task author.

For this example `answer` is set to `U*L/nu`. It is not necessary to use this specific answer, any example of a correct dimensionless group, e.g. `nu/(U*L)`, should work.

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the parameter `strict_syntax` is set to false. Since `nu` is a multi-character symbol it needs to be added as a symbol.

#### List of parameter values

- `answer`: `U*L/nu`
- `strict_syntax`: `false`

#### Examples of responses that illustrate the evaluation functions capabilities

- `U*L/nu` a valid group
- `nu/U/L` a valid group
- `U^2*L^2/nu^2` a valid group
- `U*L/nu+1` a valid group
- `8*U*L/nu` a valid group
- `q*U*L/nu` a group with an unknown symbol
- `U*L/nu, nu/U/L` two dimensionless groups that are not independent
- `U*L` group that is not dimensionless

### 2) Example where a valid sets have two groups

In this example the task is: Given $U$, $L$, $\nu$ and $f$, determine the necessary number of dimensionless groups and give one example of possible expressions for them.

This task is similar to example a) with two significant differences. First, adding $f$ means that there are now two groups required, and second the task will constructed by defining the quantities and let the function compute the rest on its own instead of supplying a reference example.

For this example an EXPRESSION response area is used with `quantities` set to `('U','(length/time)') ('L','(length)') ('nu','(length**2/time)') ('f','(1/time)')` and `answer` set to `-`.

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the parameter `strict_syntax` is set to false. Since `nu` is a multi-character symbol it needs to be added as an input symbol.

#### List of parameter values

- `answer`: `-`
- `quantities` : `('U','(length/time)') ('L','(length)') ('nu','(length**2/time)') ('f','(1/time)')`  
- `strict_syntax`: `false`

#### Examples of responses that illustrate the evaluation functions capabilities

- `U*L/nu, f*L/U` a valid set of groups
- `8*U*L/nu, f*L/U+1` a valid set of groups
- `U*L/nu+f*L/U` sum that contains two valid groups does not count as valid
- `U*L/nu+f*L/U, f*L/U` sum that contains two valid groups does count as valid if the total number of groups is sufficient
- `U*L/nu` too few groups
- `U*L/nu, f*L/U, U/f/L` too many groups
- `U*L/nu, f/U` two groups where one is not dimensionless
- `L/nu, f/U` two groups where neither group is dimensionless

### 3) Example with customised feedback messages

In this example the task is:
Suppose we are studying water waves that move under the influence of gravity. We suppose that the variables of interest are the acceleration in free fall $g$, the velocity of the wave $v$, the height of the wave $h$ and the wave length $\ell$. We also suppose that they are related by a dimensionally complete equation $f(g,v,h,\ell) = 0$. Determine the minimum number of dimensionless power products describe this problem according to the Buckingham Pi theorem and give one example of a valid set of power products.

For this problem two dimensionless groups are needed, see the worked solution at the bottom of this example for a terse solution that gives the general form of the dimensionless quantities.

For this example an EXPRESSION response area is used the answer `g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4` (this corresponds to $p_1 = 1$, $p_2 = 2$, $q_1 = 3$, $q_2 = 4$ in the worked solution shown in the examples module). The feedback was customised by setting the `custom_feedback` parameter too:  
`{`  
`    "VALID_CANDIDATE_SET": "Your list of power products satisfies the Buckingham Pi theorem."`,  
`    "NOT_DIMENSIONLESS": "At least one power product is not dimensionless."`,  
`    "MORE_GROUPS_THAN_REFERENCE_SET": "Response has more power products than necessary."`,  
`    "CANDIDATE_GROUPS_NOT_INDEPENDENT": "Power products in response are not independent."`,  
`    "TOO_FEW_INDEPENDENT_GROUPS": "Candidate set contains too few independent power products."`,  
`    "UNKNOWN_SYMBOL": "One of the power products contains an unknown symbol."`,  
`    "SUM_WITH_INDEPENDENT_TERMS": "The candidate set contains an expression which contains more independent terms than there are power products in total. The candidate set should ideally only contain expressions written as power products."`  
`}`

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the parameter `strict_syntax` is set to false.

#### List of parameter values

- `answer`: `g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4`
- `custom_feedback` : `{`  
    `"VALID_CANDIDATE_SET": "Your list of power products satisfies the Buckingham Pi theorem."`,  
    `"NOT_DIMENSIONLESS": "At least one power product is not dimensionless."`,  
    `"MORE_GROUPS_THAN_REFERENCE_SET": "Response has more power products than necessary."`,  
    `"CANDIDATE_GROUPS_NOT_INDEPENDENT": "Power products in response are not independent."`,  
    `"TOO_FEW_INDEPENDENT_GROUPS": "Candidate set contains too few independent power products."`,  
    `"UNKNOWN_SYMBOL": "One of the power products contains an unknown symbol."`,  
    `"SUM_WITH_INDEPENDENT_TERMS": "The candidate set contains an expression which contains more independent terms than there are power products in total. The candidate set should ideally only contain expressions written as power products."`  
}`
- `strict_syntax`: `false`

#### Examples of responses that illustrate the customized feedback messages

- `g*v**(-2)*h**3*l**2, g**2*v**(-4)*h**3*l` a valid set of power products
- `h*l, h**2*l**2` two power products that are not independent
- `g**1*v**2*h**3*l**4, g**4*v**3*h**2*l**1` two power products that are not dimensionless
- `g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4, g**(-1)*v**2*h` set of three power products where any two power products together creates a valid set
- `q*g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4` two power products where one has an undefined symbol, i.e. `q`
- `g**(-2)*v**4*h*l**3+g**(-2)*v**4*h**2*l**4` two power products in a sum instead of written as a set

#### Terse solution giving the general form of a valid set of groups

We have the following dimensions:
$[a] = LT^{-2}$, $[v] = LT^{-1}$, $[h] = L$, $[\ell] = L$
This gives the dimensional matrix:
$A = \begin{pmatrix} 1 & -2 \\ 1 & -1 \\ 1 & 0 \\ 1 & 0 \end{pmatrix}$
Gaussian elimination can be used to how that $r=\mathrm{rank}(A)$. With $m=3$ quantities it follows from the Buckingham Pi theorem that we need $m-r = 2$ dimensionless quantities $\pi_1$ and $\pi_2$.

For $\pi_i$, $i \in \{1,2\}$ the following holds:
$[\pi_i] = [g]^{a_i} [v]^{b_i} [h]^{c_i} [l]^{d_i} = L^{a_i+b_i+c_i+d_i} T^{-2a_i-b_i}$

$\Rightarrow \begin{cases} a_i+b_i+c_i+d_i = 0, \\ -2a_i-b_i = 0 \end{cases} \Rightarrow \begin{cases} a_i = p_i-q_i, \\ b_i = -2a_i \\ c_i = -p_i \\ d_i = -q_i \end{cases}$, where $p_i$ and $q_i$ ($i \in \{1,2\}$) are arbitrarily chosen integers. Thus $\pi_1$ and $\pi_2$ will be independent unless $\frac{a_1}{a_2} = \frac{b_1}{b_2} = \frac{c_1}{c_2} = \frac{d_1}{d_2}$ which in this case means that $\pi_i$ and $\pi_2$ are independent if $\frac{p_1}{p_2} \neq \frac{q_1}{q_2}$.
# buckinghamPiTheorem

Checks that the set of quantities in the response matches the set of quantities in the sense given by the Buckingham Pi theorem.

There are three different ways of supplying this function with the necessary information.
- In the answer, provide an example set of groups as a comma separated list. When used this way the function assumes that the given list is correct and contains at least the minimum number of groups.
- In the `quantities` parameter, supply a list of what the dimensions for each quantity is and set answer to `-`. The function will then compute a list of sufficiently many independent dimensionless quantities and compare to the response.
- In the `quantities` parameter, supply a list of what the dimensions for each quantity is and in the answer, supply a list of groups as in the first option. The function will then check that the supplied answer is dimensionless and has a sufficient number of independent groups before comparing it to the response.

Note that in lists of groups the items should ideally be written in the form $q_1^{c_1} \cdot q_2^{c_2} \cdots q_n^{c_n}$ where $q_1, q_2 \ldots q_n$ are quantities and $c_1, c_2 \ldots c_n$ are integers, but the function can also handle item that are sums with terms written in the form $a \cdot q_1^{c_1} \cdot q_2^{c_2} \cdots q_n^{c_n}$ where $q_1, q_2 \ldots q_n$ are quantities, $c_1, c_2 \ldots c_n$ rational numbers and $a$ a constant. If the total number of groups is less than required the set of groups is considered invalid, even if there is a sufficient number of terms with independent power products in the response.

## Inputs
All input parameters need to be supplied via the **Grading parameters** panel.

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

Each quantity should be written in the form `('quantity name','(units)')` and all pairs concatenated into a single string. See tables below for available default units.

Whenever units are used they must be written exactly as in the left columns of the tables given below (no short forms or single-character symbols) and units must be multiplied (or divided) by each other, as well as any accompanying quantities. 

#### Table: Base SI units

SI base units taken from Table 1 of the [NIST Guide to the SI, Chapter 4: The Two Classes of SI Units and the SI Prefixes](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-4-two-classes-si-units-and-si-prefixes)

Note that gram is used as a base unit instead of kilogram.

| SI base unit | Symbol | Dimension name      |
|--------------|:-------|:--------------------|
| metre        |   m    | length              |
| gram         |   g    | mass                |
| second       |   s    | time                |
| ampere       |   A    | electriccurrent     |
| kelvin       |   k    | temperature         |
| mole         |  mol   | amountofsubstance   |
| candela      |  cd    | luminousintensity   |

#### Table: SI prefixes

SI base units taken from Table 5 of [NIST Guide to the SI, Chapter 4: The Two Classes of SI Units and the SI Prefixes](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-4-two-classes-si-units-and-si-prefixes)

| SI Prefix | Symbol | Factor     | | SI Prefix | Symbol | Factor     |
|-----------|:-------|:-----------|-|-----------|:-------|:-----------|
| quetta    |   Q    | $10^{30}$  | | deci      |   d    | $10^{-1}$  |
| ronna     |   R    | $10^{27}$  | | centi     |   c    | $10^{-2}$  |
| yotta     |   Y    | $10^{24}$  | | milli     |   m    | $10^{-3}$  |
| zetta     |   Z    | $10^{21}$  | | micro     |   mu   | $10^{-6}$  |
| exa'      |   E    | $10^{18}$  | | nano      |   n    | $10^{-9}$  |
| peta      |   P    | $10^{15}$  | | pico      |   p    | $10^{-12}$ |
| tera      |   T    | $10^{12}$  | | femto     |   f    | $10^{-15}$ |
| giga      |   G    | $10^{9}$   | | atto      |   a    | $10^{-18}$ |
| mega      |   M    | $10^{6}$   | | zepto     |   z    | $10^{-21}$ |
| kilo      |   k    | $10^{3}$   | | yocto     |   y    | $10^{-24}$ |
| hecto     |   h    | $10^{2}$   | | ronto     |   r    | $10^{-27}$ |
| deka      |   da   | $10^{1}$   | | quecto    |   q    | $10^{-30}$ |

#### Table: Common non-SI units

Commonly used non-SI units taken from Table 6 and 7 of [NIST Guide to the SI, Chapter 5: Units Outside the SI](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-4-two-classes-si-units-and-si-prefixes)

Note that the function treats angles, neper and bel as dimensionless values.

Note that only the first table in this section has short form symbols defined, the second table does not.

| Unit name         | Symbol | Expressed in SI units                      |
|-------------------|:-------|:-------------------------------------------|
| minute            |  min   | $60~\mathrm{second}$                       |
| hour              |   h    | $3600~\mathrm{second}$                     |
| degree            |  deg   | $\frac{\pi}{180}$                          |
| liter             |   l    | $10^{-3}~\mathrm{metre}^3$                 |
| metric_ton        |   t    | $10^3~\mathrm{kilogram}$                   |
| neper             |  Np    | $1$                                        |
| bel               |   B    | $\frac{1}{2}~\ln(10)$                      |
| electronvolt      |  eV    | $1.60218 \cdot 10^{-19}~\mathrm{joule}$    |
| atomic_mass_unit  |   u    | $1.66054 \cdot 10^{-27}~\mathrm{kilogram}$ |
| angstrom          |   å    | $10^{-10}~\mathrm{metre}$                  |

| Unit name        | Expressed in SI units                                |
|------------------|:-----------------------------------------------------|
| day              | $86400~\mathrm{second}$                              |
| angleminute      | $\frac{\pi}{10800}$                                  |
| anglesecond      | $\frac{\pi}{648000}$                                 |
| astronomicalunit | $149597870700~\mathrm{metre}$                        |
| nauticalmile     | $1852~\mathrm{metre}$                                |
| knot             | $\frac{1852}{3600}~\mathrm{metre~second}^{-1}$       |
| are              | $10^2~\mathrm{metre}^2$                              |
| hectare          | $10^4~\mathrm{metre}^2$                              |
| bar              | $10^5~\mathrm{pascal}$                               |
| barn             | $10^{-28}~\mathrm{metre}$                            |
| curie            | $3.7 \cdot 10^{10}~\mathrm{becquerel}                |
| roentgen         | $2.58 \cdot 10^{-4}~\mathrm{kelvin~(kilogram)}^{-1}$ |
| rad              | $10^{-2}~\mathrm{gray}$                              |
| rem              | $10^{-2}~\mathrm{sievert}$                           |

#### Table: Imperial units

Commonly used imperial units taken from [Wikipedia: Imperial units](https://en.wikipedia.org/wiki/Imperial_units)

| Unit name         | Symbol | Expressed in SI units                         |
|-------------------|:-------|:----------------------------------------------|
| inch              |   in   | $0.0254~\mathrm{metre}$                       |
| foot              |   ft   | $0.3048~\mathrm{metre}$                       |
| yard              |   yd   | $0.9144~\mathrm{metre}$                       |
| mile              |   mi   | $1609.344~\mathrm{metre}$                     |
| fluid ounce       |  fl oz | $28.4130625~\mathrm{millilitre}$              |
| gill              |   gi   | $142.0653125~\mathrm{millilitre}$             |
| pint              |   pt   | $568.26125~\mathrm{millilitre}$               |
| quart             |   qt   | $1.1365225~\mathrm{litre}$                    |
| gallon            |   gal  | $4546.09~\mathrm{litre}$                      |
| ounce             |   oz   | $28.349523125~\mathrm{gram}$                  |
| pound             |   lb   | $0.45359237~\mathrm{kilogram}$                |
| stone             |   st   | $6.35029318~\mathrm{kilogram}$                |

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

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the grading parameter `strict_syntax` is set to false. Since `nu` is a multicharacter symbol it needs to be added as an input symbol.

#### b)

In this example the task is: Given $U$, $L$, $\nu$ and $f$, determine the necessary number of dimensionless groups and give one example of possible expressions for them.

This task is similar to example a) with two significant differences. First, adding $f$ means that there are now two groups required, and second the task will constructed by defining the quantities and let the function compute the rest on its own instead of supplying a reference example.

For this example an EXPRESSION response area is used with `quantities` set to `('U','(length/time)') ('L','(length)') ('nu','(length**2/time)') ('f','(1/time)')` and `answer` set to `-`.

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the grading parameter `strict_syntax` is set to false. Since `nu` is a multicharacter symbol it needs to be added as an input symbol.

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

With default settings it is required to put `*` (or `/`) between each part of the response and answer. To remove this requirement the grading parameter `strict_syntax` is set to false.
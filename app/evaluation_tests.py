import unittest

from .evaluation import (
    evaluation_function,
    buckingham_pi_feedback_responses,
    parsing_feedback_responses
)


class TestEvaluationFunction(unittest.TestCase):
    """
    TestCase Class used to test the algorithm.
    ---
    Tests are used here to check that the algorithm written
    is working as it should.

    It's best practise to write these tests first to get a
    kind of 'specification' for how your algorithm should
    work, and you should run these tests before committing
    your code to AWS.

    Read the docs on how to use unittest here:
    https://docs.python.org/3/library/unittest.html

    Use evaluation_function() to check your algorithm works
    as it should.
    """

    def assertEqual_input_variations(self, response, answer, params, value):
        with self.subTest(response=response, answer=answer):
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), value)
        variation_definitions = [lambda x: x.replace('**', '^'),
                                 lambda x: x.replace('**', '^').replace('*', ' '),
                                 lambda x: x.replace('**', '^').replace('*', '')]
        for variation in variation_definitions:
            response_variation = variation(response)
            answer_variation = variation(answer)
            if (response_variation != response) or (answer_variation != answer):
                with self.subTest(response=response_variation, answer=answer):
                    result = evaluation_function(response_variation, answer, params)
                    self.assertEqual(result.get("is_correct"), value)
                with self.subTest(response=response, answer=answer_variation):
                    result = evaluation_function(response, answer_variation, params)
                    self.assertEqual(result.get("is_correct"), value)
                with self.subTest(response=response_variation, answer=answer_variation):
                    result = evaluation_function(response_variation, answer_variation, params)
                    self.assertEqual(result.get("is_correct"), value)

    def test_buckingham_pi_one_group(self):
        answer = "U*L/nu"
        params = {
            "symbols": {
                "nu": {"latex": r"\(\nu\)", "aliases": []},
                "L": {"latex": r"\(L\)", "aliases": []},
                "U": {"latex": r"\(U\)", "aliases": []},
            },
            "strict_syntax": False
        }
        correct_responses = ["U*L/nu",
                             "L*U/nu",
                             "nu/U/L",
                             "(U*L/nu)**2",
                             "2*U*L/nu"]
        incorrect_responses = ["U*L/n/u",
                               "1",
                               "U*L*nu",
                               "A*U*L/nu",
                               "A",
                               "U/nu",
                               "U*L"]
        for response in correct_responses:
            self.assertEqual_input_variations(response, answer, params, True)
        for response in incorrect_responses:
            self.assertEqual_input_variations(response, answer, params, False)

    def test_warning_inappropriate_symbol(self):
        params = {
            "symbols": {
                "nu": {"latex": r"\(\nu\)", "aliases": []},
                "L": {"latex": r"\(L\)", "aliases": []},
                "U": {"latex": r"\(U\)", "aliases": []},
            },
            'strict_syntax': True
        }

        with self.subTest(tag="^ in response"):
            answer = "U*L/nu"
            response = "U^2*L^2/nu^2"
            result = evaluation_function(response, answer, params)
            self.assertEqual(parsing_feedback_responses["PARSE_ERROR_WARNING"](response) in result["feedback"], True)
            self.assertEqual(parsing_feedback_responses["STRICT_SYNTAX_EXPONENTIATION"] in result["feedback"], True)

        with self.subTest(tag="^ in answer"):
            answer = "U^2*L^2/nu^2"
            response = "U*L/nu"
            self.assertRaises(
                Exception,
                evaluation_function,
                response,
                answer,
                params,
            )


    def test_buckingham_pi_unknown_symbols(self):
        answer = "a*b*c"
        params = {
            "symbols": {
                "a": {"latex": r"\(a\)", "aliases": []},
                "b": {"latex": r"\(b\)", "aliases": []},
                "c": {"latex": r"\(c\)", "aliases": []},
            },
            "strict_syntax": False
        }
        response = "a*b*c*p*q"
        self.assertEqual_input_variations(response, answer, params, False)
        result = evaluation_function(response, answer, params)
        self.assertEqual(
            buckingham_pi_feedback_responses["UNKNOWN_SYMBOL"](["$p$", "$q$"]) in result["feedback"]
            or
            buckingham_pi_feedback_responses["UNKNOWN_SYMBOL"](["$q$", "$p$"]) in result["feedback"],
            True
        )

    def test_buckingham_pi_two_groups_with_custom_feedback(self):
        # For this test we use the following quantities
        #  [g] = L/T**2
        #  [v] = L/T
        #  [h] = L
        #  [l] = L
        # This gives dimensional matrix
        #     --  --
        #     |1 -2|
        #     |1 -1|
        # A = |1  0|
        #     |1  0|
        #     --  --
        # This matrix has rank 2 and the two groups can be written on the form
        # pi1 = g**(p1-q1) * v**(2*q1-2*p1) * h**(p1) * l**(q1)
        # pi2 = g**(p2-q2) * v**(2*q2-2*p2) * h**(p2) * l**(q2)
        # The two groups are independent unless p1/p2 = q1/q2
        params = {
            "strict_syntax": False,
            "symbols": {
                "g": {"latex": r"\(g\)", "aliases": []},
                "l": {"latex": r"\(l\)", "aliases": []},
                "v": {"latex": r"\(v\)", "aliases": []},
                "h": {"latex": r"\(h\)", "aliases": []},
            },
            "custom_feedback": {
                "VALID_CANDIDATE_SET": "Your list of power products satisfies the Buckingham Pi theorem.",
                "NOT_DIMENSIONLESS": "At least one power product is not dimensionless.",
                "MORE_GROUPS_THAN_REFERENCE_SET": "Response has more power products than necessary.",
                "CANDIDATE_GROUPS_NOT_INDEPENDENT": "Power products in response are not independent.",
                "TOO_FEW_INDEPENDENT_GROUPS": "Candidate set contains too few independent groups.",
                "UNKNOWN_SYMBOL": "One of the prower products contains an unkown symbol.",
                "SUM_WITH_INDEPENDENT_TERMS": "The candidate set contains an expression which contains more independent terms that there are groups in total. The candidate set should ideally only contain expressions written as power products."
            }
        }
        with self.subTest(tag="Valid response"):
            # This corresponds to p1 = 1, p2 = 2, q1 = 3, q2 = 4
            answer = "g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4"
            # This corresponds to p1 = 3, p2 = 3, q1 = 2, q2 = 1
            response = "g*v**(-2)*h**3*l**2, g**2*v**(-4)*h**3*l"
            self.assertEqual_input_variations(response, answer, params, True)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["VALID_CANDIDATE_SET"] in result["feedback"], True)
        with self.subTest(tag="Too few independent groups"):
            # This corresponds to p1 = 1, p2 = 2, q1 = 1, q2 = 2
            response = "h*l, h**2*l**2"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["CANDIDATE_GROUPS_NOT_INDEPENDENT"] in result["feedback"], True)
            self.assertEqual(params["custom_feedback"]["TOO_FEW_INDEPENDENT_GROUPS"] in result["feedback"], True)
        with self.subTest(tag="Not dimensionless"):
            # This does not correspond to any consistent values of p1, p2, q1 and q2
            response = "g**1*v**2*h**3*l**4, g**4*v**3*h**2*l**1"
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["NOT_DIMENSIONLESS"] in result["feedback"], True)
            self.assertEqual_input_variations(response, answer, params, False)
        with self.subTest(tag="Extra dimensionless group"):
            # This adds an extra dimensionless group
            response = "g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4, g**(-1)*v**2*h"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["MORE_GROUPS_THAN_REFERENCE_SET"] in result["feedback"], True)
        with self.subTest(tag="Undefined symbol"):
            # This is a response with an undefined symbol added
            response = "q*g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["UNKNOWN_SYMBOL"] in result["feedback"], True)
        with self.subTest(tag="Sum with independent terms instead of set of groups"):
            # This is a response with the two groups in a valid set in sum instead of a comma-separated list
            response = "g**(-2)*v**4*h*l**3+g**(-2)*v**4*h**2*l**4"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["SUM_WITH_INDEPENDENT_TERMS"] in result["feedback"], True)

    def test_buckingham_pi_too_many_groups(self):
        # This test uses the same groups as 'test_buckingham_pi_two_groups_with_custom_feedback'
        params = {
            "strict_syntax": False,
            "symbols": {
                "g": {"latex": r"\(g\)", "aliases": []},
                "l": {"latex": r"\(l\)", "aliases": []},
                "v": {"latex": r"\(v\)", "aliases": []},
                "h": {"latex": r"\(h\)", "aliases": []},
            },
        }
        answer = "g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4"
        response = "g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4, g**(-1)*v**2*h"
        self.assertEqual_input_variations(response, answer, params, False)
        result = evaluation_function(response, answer, params)
        self.assertEqual(buckingham_pi_feedback_responses["MORE_GROUPS_THAN_REFERENCE_SET"] in result["feedback"], True)

    def test_buckingham_pi_two_groups_with_quantities(self):
        params = {
            "strict_syntax": False,
            "quantities": "('U', '(length/time)') ('L', '(length)') ('nu', '(length**2/time)') ('f', '(1/time)')",
            "symbols": {
                "U": {"latex": r"\(U\)", "aliases": []},
                "L": {"latex": r"\(L\)", "aliases": []},
                "nu": {"latex": r"\(\nu\)", "aliases": []},
                "f": {"latex": r"\(f\)", "aliases": []},
            },
        }
        answer = "U*L/nu, f*L/U"
        response = "U*L/nu, nu/(f*L**2)"
        self.assertEqual_input_variations(response, answer, params, True)

    def test_buckingham_pi_two_groups_with_quantities_no_answer(self):
        params = {
            "strict_syntax": False,
            "quantities": "('U', '(length/time)') ('L', '(length)') ('nu', '(length**2/time)') ('f', '(1/time)')",
            "symbols": {
                "U": {"latex": r"\(U\)", "aliases": []},
                "L": {"latex": r"\(L\)", "aliases": []},
                "nu": {"latex": r"\(\nu\)", "aliases": []},
                "f": {"latex": r"\(f\)", "aliases": []},
            },
        }
        answer = "-"
        response = "U*L/nu, nu/(f*L**2)"
        self.assertEqual_input_variations(response, answer, params, True)
        response = "U*L/nu, f*L/U"
        self.assertEqual_input_variations(response, answer, params, True)

    def test_buckingham_pi_two_groups_with_quantities_not_dimensionless(self):
        params = {
            "strict_syntax": False,
            "quantities": "('U', '(length/time)') ('L', '(length)') ('nu', '(length**2/time)') ('f', '(1/time)')",
            "symbols": {
                "U": {"latex": r"\(U\)", "aliases": []},
                "L": {"latex": r"\(L\)", "aliases": []},
                "nu": {"latex": r"\(\nu\)", "aliases": []},
                "f": {"latex": r"\(f\)", "aliases": []},
            },
        }
        answer = "f*U*L/nu, f*L/U"
        response = "U*L/nu, nu/(f*L**2)"
        self.assertRaises(
            Exception,
            evaluation_function,
            response,
            answer,
            params,
        )
        answer = "U*L/nu, f*L/U"
        response = "U*L/nu, U*nu/(f*L**2)"
        result = evaluation_function(response, answer, params)
        self.assertEqual(buckingham_pi_feedback_responses["NOT_DIMENSIONLESS"]({"$\frac{LU}{\nu}", }) in result["feedback"], True)

    def test_buckingham_pi_two_groups_with_quantities_too_few_independent_groups_in_answer(self):
        params = {
            "strict_syntax": False,
            "quantities": "('U', '(length/time)') ('L', '(length)') ('nu', '(length**2/time)') ('f', '(1/time)')",
            "symbols": {
                "U": {"latex": r"\(U\)", "aliases": []},
                "L": {"latex": r"\(L\)", "aliases": []},
                "nu": {"latex": r"\(\nu\)", "aliases": []},
                "f": {"latex": r"\(f\)", "aliases": []},
            },
        }
        answer = "U*L/nu"
        response = "U*L/nu, nu/(f*L**2)"
        self.assertRaises(
            Exception,
            evaluation_function,
            response,
            answer,
            params,
        )
        answer = "U*L/nu, (U*L/nu)**2"
        response = "U*L/nu, nu/(f*L**2)"
        self.assertRaises(
            Exception,
            evaluation_function,
            response,
            answer,
            params,
        )

    def test_buckingham_pi_two_groups_with_quantities_with_dependent_groups_in_response(self):
        params = {
            "strict_syntax": False,
            "quantities": "('U', '(length/time)') ('L', '(length)') ('nu', '(length**2/time)') ('f', '(1/time)')",
            "symbols": {
                "U": {"latex": r"\(U\)", "aliases": []},
                "L": {"latex": r"\(L\)", "aliases": []},
                "nu": {"latex": r"\(\nu\)", "aliases": []},
                "f": {"latex": r"\(f\)", "aliases": []},
            },
        }
        answer = "U*L/nu, f*L/U"
        response = "U*L/nu, (U*L/nu)**2"
        self.assertEqual_input_variations(response, answer, params, False)
        result = evaluation_function(response, answer, params)
        self.assertEqual(buckingham_pi_feedback_responses["CANDIDATE_GROUPS_NOT_INDEPENDENT"](1, 2) in result["feedback"], True)
        self.assertEqual(buckingham_pi_feedback_responses["TOO_FEW_INDEPENDENT_GROUPS"]("Response", 1, 2) in result["feedback"], True)

    def test_buckingham_pi_three_groups_with_quantities_with_too_few_independent_groups_in_response(self):
        params = {
            "strict_syntax": False,
            "quantities": "('f', '(1/second)') ('l', '(metre)') ('U', '(metre/second)') ('h', '(metre)') ('Re', '(1)')",
            "symbols": {
                "f": {"latex": r"\(f\)", "aliases": []},
                "l": {"latex": r"\(l\)", "aliases": []},
                "U": {"latex": r"\(U\)", "aliases": []},
                "Re": {"latex": r"\(\mathrm{Re}\)", "aliases": []},
                "h": {"latex": r"\(h\)", "aliases": []},
            }
        }
        answer = "f*l/U, h/l, 1/Re"
        response = "fl/U, h/l"
        self.assertEqual_input_variations(response, answer, params, False)
        result = evaluation_function(response, answer, params)
        self.assertEqual(buckingham_pi_feedback_responses["TOO_FEW_INDEPENDENT_GROUPS"]("Response", 2, 3) in result["feedback"], True)

    def test_buckingham_pi_sum_with_dimensional_term(self):
        params = {
            "strict_syntax": False,
        }
        answer = "v/(f*l)"
        response = "v/(fl)+v"
        self.assertEqual_input_variations(response, answer, params, False)

    def test_fractional_powers_buckingham_pi(self):
        params = {"strict_syntax": False}
        with self.subTest(tag="square root in answer"):
            answer = "f*(((m*l)/T)**0.5)"
            response = "f**2*((m*l)/T)"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)

        with self.subTest(tag="fractional power that can be written exactly as a decimal in answer"):
            answer = "f*(((m*l)/T)**0.25)"
            response = "f**4*((m*l)/T)"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)

        with self.subTest(tag="fractional power written as a fraction in answer"):
            answer = "f*(((m*l)/T)**(1/3))"
            response = "f**3*((m*l)/T)"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)

        with self.subTest(tag="fractional power that that is not an n:th root in answer"):
            answer = "f*(((m*l)/T)**(2/3))"
            response = "f**3*((m*l)/T)**2"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)

    def test_sums_buckingham_pi(self):
        params = {"strict_syntax": False}

        with self.subTest(tag="sum of valid dimensionless terms"):
            answer = "f*(((m*l)/T)**0.5)"
            response = "5*f**2*((m*l)/T)+sin(10)*f*((m*l)/T)**0.5+1"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)

        with self.subTest(tag="sum that contains an invalid dimensionless terms"):
            answer = "f*(((m*l)/T)**0.5)"
            response = "f**2*((m*l)/T)+((m*l)/T)**0.5+1"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)

        params = {
            "strict_syntax": False,
            "quantities": "('F', '(gram*metre*second**(-2))') ('U', '(metre/second)') ('rho', '(gram/(metre**3))') ('D', '(metre)') ('omega', '(second**(-1))')",
            "symbols": {
                    'U': {"latex": r"$U$", "aliases": []},
                    'F': {"latex": r"$F$", "aliases": []},
                    'D': {"latex": r"$D$", "aliases": []},
                    'rho': {"latex": r"$\rho$", "aliases": []},
                    'omega': {"latex": r"$\omega$", "aliases": []},
                }
        }

        with self.subTest(tag="two groups, one is sum of valid terms"):
            answer = "-"
            response = "U/(omega*D), U/(omega*D)+F/(rho*D**4*omega**2)"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)

        with self.subTest(tag="two groups, one has an invalid terms"):
            answer = "-"
            response = "U/(omega*D), U/(omega*D)+1/(rho*D**4*omega**2)"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)

        with self.subTest(tag="a sum with two independent valid terms instead of two groups"):
            answer = "-"
            response = "U/(omega*D)+F/(rho*D**4*omega**2)"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)
            self.assertEqual(buckingham_pi_feedback_responses["SUM_WITH_INDEPENDENT_TERMS"]("response") in result["feedback"], True)

    def test_buckingham_pi_example_in_examples_module(self):
        with self.subTest(tag="Part a)"):
            params = {
                "strict_syntax": False,
                "quantities": "('U', '(length/time)') ('L', '(length)') ('nu', '(length**2/time)')",
                "symbols": {
                    'U': {"latex": r"$U$", "aliases": []},
                    'L': {"latex": r"$L$", "aliases": []},
                    'nu': {"latex": r"$\nu$", "aliases": []},
                }
            }
            answer = "U*L/nu"
            # Valid groups
            response = "U*L/nu"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)
            response = "U*L/nu+1"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)
            response = "8*U*L/nu"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)
            # A group with an unknown symbol
            response = "q*U*L/nu"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)
            self.assertEqual(buckingham_pi_feedback_responses["UNKNOWN_SYMBOL"]({"$q$"}) in result["feedback"], True)
            # two dimensionless groups that are not independent
            response = "U*L/nu, nu/U/L"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)
            self.assertEqual(buckingham_pi_feedback_responses["CANDIDATE_GROUPS_NOT_INDEPENDENT"](1, 2) in result["feedback"], True)
            self.assertEqual(buckingham_pi_feedback_responses["MORE_GROUPS_THAN_REFERENCE_SET"] in result["feedback"], True)
            # group that is not dimensionless
            response = "U*L"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)
            self.assertEqual(buckingham_pi_feedback_responses["NOT_DIMENSIONLESS"]({"$L U$", }) in result["feedback"], True)
        with self.subTest(tag="Part b)"):
            params = {
                "strict_syntax": False,
                "quantities": "('U', '(length/time)') ('L', '(length)') ('nu', '(length**2/time)') ('f', '(1/time)')",
                "symbols": {
                    'U': {"latex": r"$U$", "aliases": []},
                    'L': {"latex": r"$L$", "aliases": []},
                    'nu': {"latex": r"$\nu$", "aliases": []},
                    'f': {"latex": r"$f$", "aliases": []},
                }
            }
            answer = "-"
            # Valid groups
            response = "U*L/nu, f*L/U"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)
            response = "8*U*L/nu, f*L/U+1"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)
            # sum that contains two valid groups does not count as valid
            response = "U*L/nu+f*L/U"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)
            self.assertEqual(buckingham_pi_feedback_responses["SUM_WITH_INDEPENDENT_TERMS"]("response") in result["feedback"], True)
            # sum that contains two valid groups does count as valid if the total number of groups is sufficient
            response = "U*L/nu+f*L/U, f*L/U"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], True)
            # at least one group is not dimensionless
            response = "U*L/nu, f/U"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)
            self.assertEqual(buckingham_pi_feedback_responses["NOT_DIMENSIONLESS"]({r"$\frac{f}{U}$"}) in result["feedback"], True)
            response = "L/nu, f/U"
            result = evaluation_function(response, answer, params)
            self.assertEqual(result["is_correct"], False)
            self.assertEqual(
                buckingham_pi_feedback_responses["NOT_DIMENSIONLESS"]([r"$\frac{L}{\nu}$", r"$\frac{f}{U}$"]) in result["feedback"]
                or
                buckingham_pi_feedback_responses["NOT_DIMENSIONLESS"]([r"$\frac{f}{U}$", r"$\frac{L}{\nu}$"]) in result["feedback"],
                True
            )
        with self.subTest(tag="Part c)"):
            params = {
                "strict_syntax": False,
                "symbols": {
                    'g': {"latex": r"$g$", "aliases": []},
                    'v': {"latex": r"$v$", "aliases": []},
                    'h': {"latex": r"$h$", "aliases": []},
                    'l': {"latex": r"$l$", "aliases": []},
                },
                "custom_feedback": {
                    "VALID_CANDIDATE_SET": "Your list of power products satisfies the Buckingham Pi theorem.",
                    "NOT_DIMENSIONLESS": "At least one power product is not dimensionless.",
                    "MORE_GROUPS_THAN_REFERENCE_SET": "Response has more power products than necessary.",
                    "CANDIDATE_GROUPS_NOT_INDEPENDENT": "Power products in response are not independent.",
                    "TOO_FEW_INDEPENDENT_GROUPS": "Candidate set contains too few independent groups.",
                    "UNKNOWN_SYMBOL": "One of the prower products contains an unkown symbol.",
                    "SUM_WITH_INDEPENDENT_TERMS": "The candidate set contains an expression which contains more independent terms that there are groups in total. The candidate set should ideally only contain expressions written as power products."
                }
            }
            answer = "g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4"
            # Valid response
            response = "g*v**(-2)*h**3*l**2, g**2*v**(-4)*h**3*l"
            self.assertEqual_input_variations(response, answer, params, True)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["VALID_CANDIDATE_SET"] in result["feedback"], True)
            # Too few independent groups
            response = "h*l, h**2*l**2"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["CANDIDATE_GROUPS_NOT_INDEPENDENT"] in result["feedback"], True)
            self.assertEqual(params["custom_feedback"]["TOO_FEW_INDEPENDENT_GROUPS"] in result["feedback"], True)
            # Not dimensionless
            response = "g**1*v**2*h**3*l**4, g**4*v**3*h**2*l**1"
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["NOT_DIMENSIONLESS"] in result["feedback"], True)
            self.assertEqual_input_variations(response, answer, params, False)
            # Extra dimensionless group
            response = "g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4, g**(-1)*v**2*h"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["MORE_GROUPS_THAN_REFERENCE_SET"] in result["feedback"], True)
            # Undefined symbol
            response = "q*g**(-2)*v**4*h*l**3, g**(-2)*v**4*h**2*l**4"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["UNKNOWN_SYMBOL"] in result["feedback"], True)
            # Sum with independent terms instead of set of groups
            response = "g**(-2)*v**4*h*l**3+g**(-2)*v**4*h**2*l**4"
            self.assertEqual_input_variations(response, answer, params, False)
            result = evaluation_function(response, answer, params)
            self.assertEqual(params["custom_feedback"]["SUM_WITH_INDEPENDENT_TERMS"] in result["feedback"], True)

    def test_MECH50010_set_5(self):
        # Dimensional homogeneity a)
        params = {"strict_syntax": False}
        answer = "f*(((m*l)/T)**0.5)"
        response = "f**2*((m*l)/T)"
        result = evaluation_function(response, answer, params)
        self.assertEqual(result["is_correct"], True)

        # Aircraft propeller a)
        params = {
            "strict_syntax": False,
            "quantities": "('F', '(gram*metre*second**(-2))') ('U', '(metre/second)') ('rho', '(gram/(metre**3))') ('D', '(metre)') ('omega', '(second**(-1))')",
            "symbols": {
                "F": {"latex": r"\(F\)", "aliases": []},
                "U": {"latex": r"\(U\)", "aliases": []},
                "rho": {"latex": r"\(\rho\)", "aliases": []},
                "D": {"latex": r"\(D\)", "aliases": []},
                "omega": {"latex": r"\(\omega\)", "aliases": []},
            }
        }
        answer = "-"
        response = "U/(omega*D), F/(rho*D**4*omega**2)"
        result = evaluation_function(response, answer, params)
        self.assertEqual(result["is_correct"], True)

        response = "U/(omega*D), F/(rho*D**2*U**2)"
        result = evaluation_function(response, answer, params)
        self.assertEqual(result["is_correct"], True)

        response = "F/(rhoD^4omega^2)"
        result = evaluation_function(response, answer, params)
        self.assertEqual(result["is_correct"], False)

        # Drag on a ship a)
        params = {
            "strict_syntax": False,
            "quantities": "('mu', '(gram/metre/second)') ('F', '(gram*metre*second**(-2))') ('U', '(metre/second)') ('rho', '(gram/(metre**3))') ('l', '(metre)') ('B', '(metre)') ('g', '(metre*second**(-2))') ",
            "symbols": {
                'F': {"latex": r"$F$", "aliases": ["FD", "fd", "Fd", "F_D", "F_d"]},
                'U': {"latex": r"$U$", "aliases": ["u"]},
                'l': {"latex": r"$l$", "aliases": ["L"]},
                'B': {"latex": r"$B$", "aliases": ["b", "w", "W", "width", "beam"]},
                'g': {"latex": r"$g$", "aliases": ["G"]},
                'rho': {"latex": r"$\rho$", "aliases": ["r", "Rho"]},
                'mu': {"latex": r"$\mu$", "aliases": ["m"]},
            }
        }
        answer = "-"
        response = "U*(rho)^(1/3) / (mu*g)^(1/3)"
        result = evaluation_function(response, answer, params)
        self.assertEqual(result["is_correct"], False)

    def test_eval_function_can_handle_latex_input_with_comma(self):
        response = r"\frac{m}{\left(\rho l^{3}\right)}, \frac{v t}{l}"
        answer = "-"
        params = {
            "strict_syntax": False,
            "is_latex": True,
            "symbols": {
                "m": {"latex": r"\(m\)", "aliases": []},
                "rho": {"latex": r"\(\rho\)", "aliases": []},
                "l": {"latex": r"\(l\)", "aliases": []},
                "t": {"latex": r"\(t\)", "aliases": []},
                "v": {"latex": r"\(v\)", "aliases": []},
            },
            "quantities": "('m', '(mass)') ('l', '(length)') ('rho', '(mass/(length**3))') ('v', '(length/time)') ('t', '(time)')",
        }
        result = evaluation_function(response, answer, params)
        self.assertEqual(result["is_correct"], True)


if __name__ == "__main__":
    unittest.main()

import unittest

from .preview import preview_function


class TestPreviewFunction(unittest.TestCase):
    """
    TestCase Class used to test the algorithm.
    ---
    Tests are used here to check that the algorithm written
    is working as it should.

    It's best practice to write these tests first to get a
    kind of 'specification' for how your algorithm should
    work, and you should run these tests before committing
    your code to AWS.

    Read the docs on how to use unittest here:
    https://docs.python.org/3/library/unittest.html

    Use preview_function() to check your algorithm works
    as it should.
    """

    def test_buckingham_pi_one_group(self):
        params = {"strict_syntax": False}
        response = "A/r**2"
        result = preview_function(response, params)
        self.assertEqual(result["preview"]["latex"], r"~\mathrm{A} ~\mathrm{r}^{-2}")

    def test_buckingham_pi_two_groups(self):
        params = {
            "quantities": "('U','(length/time)') ('L','(length)') ('nu','(length**2/time)') ('f','(1/time)')",
            "strict_syntax": False
        }
        response = "U*L/nu, (f*L)/U"
        result = preview_function(response, params)
        self.assertEqual(result["preview"]["latex"], "\\frac{L U}{\\nu},~\\frac{L f}{U}")


if __name__ == "__main__":
    unittest.main()

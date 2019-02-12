"""
Unit test template.

This file belongs in cryptorandom/tests
"""
# import stuff from __future__ so Python 2.7 users can run our Python 3 code
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

# We use numpy's testing module.
import numpy as np

# We use nose.tools to check for certain types of errors
from nose.tools import assert_raises, raises

# You need to do a relative import using the ".." here
from ..module import add

# Tests are written as functions with the word "test" at the beginning.
# nosetest looks for all functions with "test" in the name and runs them.
# Write two unit tests for the add function you wrote.

def test_add():
    result = add(1, 3)
    expected = 4
    np.testing.assert_equal(result, expected)
    
    # there are various np.testing functions that will be helpful for testing "almost equal", testing that arrays are the same, etc.
    # This is just one case that uses the default parameters. You should test all the possible cases!


def test_add_edge_case():
    # Test edge cases where you know the expected result
    # if you can come up with them.
    result = add("hi ", "world")
    expected = "hi world"
    np.testing.assert_equal(result, expected)


@raises(ValueError)
def test_add_error():
    # To check that it's giving the right errors, you should put what is called a decorator in the line above the function definition.
    # Then just run the function in a way you expect to throw the error.
    add("hello", 8)

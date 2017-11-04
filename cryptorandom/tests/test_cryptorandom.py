from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import numpy as np
from nose.tools import assert_raises, raises
from ..cryptorandom import BaseRandom, SHA256

def test_SHA256():
    """
    Test that SHA256 prng is instantiated correctly
    """
    r = SHA256(5)
    assert(repr(r) == 'SHA256 PRNG with seed 5 and counter 0')
    assert(str(r) == 'SHA256 PRNG with seed 5 and counter 0')
    
    assert(r.getstate() == (5, 0))
    r.next()
    assert(r.getstate() == (5, 1))
    r.jumpahead(5)
    assert(r.getstate() == (5, 6))
    r.seed(22, 3)
    assert(r.getstate() == (22, 3))
    
    
def test_SHA256_random():
    """
    Test that SHA256 PRNs are correct.
    The following tests match the output of Ron's and Philip's implementations.
    """
    r = SHA256(12345678901234567890)
    r.next()
    e1 = int("4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1", 16)
    e2 = int("ae230ec16bee77f77c7378f4eb5d265d931665e29e8bbee7e733f58d3815d338", 16)
    expected = np.array([e1, e2]) * 2**-256
    assert((r.random(2) == expected).all())
    
    r = SHA256()
    r.seed(12345678901234567890, 1)
    assert(r.random() == expected[0])

def test_SHA256_randint():
    """
    Test that SHA256 random integers are correct.
    The following tests match the output of Ron's and Philip's implementations.
    """    
    
    r = SHA256(12345678901234567890)
    r.next()
    expected = int("4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1", 16)
    assert(r.nextRandom() == expected)
    
    r = SHA256(12345678901234567890)
    fiverand = r.randint(1, 1001, 5)
    assert( (fiverand == np.array([405, 426, 921, 929,  56])).all() )
    
    r = SHA256(12345678901234567890)
    onerand = r.randint(1, 1001)
    assert(onerand == fiverand[0])
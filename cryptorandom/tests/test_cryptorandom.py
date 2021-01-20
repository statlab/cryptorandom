"""Unit tests for cryptorandom PRNG"""

import numpy as np
from ..cryptorandom import SHA256, int_from_hash

def test_SHA256():
    """
    Test that SHA256 prng is instantiated correctly
    """
    r = SHA256(5)
    assert repr(r) == 'SHA256 PRNG. seed: 5 counter: 0 randbits_remaining: 0'
    assert str(r) == 'SHA256 PRNG. seed: 5 counter: 0 randbits_remaining: 0'

    assert r.getstate() == (5, 0, 0)
    r.next()
    assert r.getstate() == (5, 1, 0)
    r.jumpahead(5)
    assert r.getstate() == (5, 6, 0)
    r.seed(22)
    assert r.getstate() == (22, 0, 0)
    r.setstate(2345, 3)
    assert r.getstate() == (2345, 3, 0)
    r.randint(0, 100, 2)
    assert r.getstate() == (2345, 4, 242)

def test_SHA256_random():
    """
    Test that SHA256 PRNs are correct.
    The following tests match the output of Ron's and Philip's implementations.
    """

    r = SHA256(12345678901234567890)
    r.next()
    expected = b'1\r\x95\x9c\xe6Tvdz>\xc90t\xbe\xff\n\xa6\xd7 \x94\x92\x07\xda\xf9\x15q/\xd5tcQe'
    assert r.nextRandom() == expected

    r = SHA256(12345678901234567890)
    r.next()
    e1 = b'1\r\x95\x9c\xe6Tvdz>\xc90t\xbe\xff\n\xa6\xd7 \x94\x92\x07\xda\xf9\x15q/\xd5tcQe'
    e2 = b'\x95\xa9\xe6,IEZ\xe0\xbf\xce\xa9\x84\x9fo\xf0\x96\x01Q$\xb8\xa0\xd7\xd0\xa9\xdf' \
        + b'\xd4Q\xc5\xfa\xfa"\xb7'
    expected = np.array(int_from_hash([e1, e2])) * 2**-256
    assert (r.random(2) == expected).all()

    r = SHA256()
    r.setstate(12345678901234567890, 1)
    assert r.random() == expected[0]

def test_SHA256_randint():
    """
    Test that SHA256 random integers are correct.
    The tests for next() and randint_trunc() match the output of Ron's and Philip's implementations.
    """
    r = SHA256(12345678901234567890)
    fiverand = r.randint_trunc(1, 1001, 5)
    assert (fiverand == np.array([876, 766, 536, 423, 164])).all()

    r = SHA256(12345678901234567890)
    onerand = r.randint_trunc(1, 1001)
    assert onerand == fiverand[0]

    r = SHA256(12345678901234567890)
    s = SHA256(12345678901234567890)
    t = int_from_hash(s.nextRandom())
    v = np.array([0]*5, dtype=int)
    inx = 0
    while inx < 5:
        u = t & int(2**10-1)
        while u > 1000:
            t = (t >> 10)
            u = t & int(2**10-1)
        v[inx] = int(u)+1
        t = (t >> 10)
        inx = inx+1
    fiverand = r.randint(1, 1001, 5)

    assert (fiverand == v).all()

    r = SHA256(12345678901234567890)
    onerand = r.randint(1, 1001)
    assert onerand == fiverand[0]


def test_SHA256_bits():
    """
    Test that SHA256 randint uses bits correctly
    """
    r = SHA256(12345678901234567890)
    s = SHA256(12345678901234567890)
    v = s.nextRandom()
    cumbits = 0
    for k in [10, 20, 30]:   # check that bits are "consumed" correctly
        val = r.getrandbits(k)
        assert val == (int_from_hash(v) >> cumbits & int(2**k - 1))
        cumbits = cumbits + k

    r = SHA256(12345678901234567890)
    s = SHA256(12345678901234567890)
    val = r.getrandbits(500)
    v = int_from_hash(s.nextRandom())
    w = int_from_hash(s.nextRandom())
    # check that blocks are appended correctly
    assert  val == ((w<<256 | v) & int(2**500 - 1))

    r = SHA256(12345678901234567890)
    val = r.randbelow_from_randbits(5)
    assert val == 3

"""
SHA-256 PRNG prototype in Python
"""

from __future__ import division
import numpy as np
import sys
import struct
# Import base class for PRNGs
import random
# Import library of cryptographic hash functions
import hashlib

# Define useful constants
BPF = 53        # Number of bits in a float
RECIP_BPF = 2**-BPF
HASHLEN = 256 # Number of bits in a hash output
RECIP_HASHLEN = 2**-HASHLEN

################################################################################
############################## Int from Hash ###################################
################################################################################

def int_from_hash_py2(hash):
    '''
    Convert byte(s) to ints, specific for Python versions < 3.

    Parameters
    ----------
    hash : bytes
        Hash or list of hashes to convert to integers

    Returns
    -------
    int or list ndarray of ints
    '''
    if isinstance(hash, list):
        hash_int = np.array([int(h.encode('hex'), 16) for h in hash])
    else:
        hash_int = int(hash.encode('hex'), 16)
    return hash_int


def int_from_hash_py3(hash):
    '''
    Convert byte(s) to ints, specific for Python 3.

    Parameters
    ----------
    hash : bytes
        Hash or list of hashes to convert to integers

    Returns
    -------
    int or list ndarray of ints
    '''
    if isinstance(hash, list):
        hash_int = np.array([int.from_bytes(h, 'big') for h in hash])
    else:
        hash_int = int.from_bytes(hash, 'big')
    return hash_int


if sys.version_info[0] < 3:
    int_from_hash = int_from_hash_py2
else:
    int_from_hash = int_from_hash_py3

################################################################################
############################## Base PRNG Class #################################
################################################################################

class BaseRandom(random.Random):
    '''Random number generator base class'''

    def __init__(self, seed=None):
        """Initialize an instance.

        Optional argument seed controls seeding, as for Random.seed().
        """

        self.seed(seed)


    def seed(self, baseseed=None, counter=0):
        """Initialize internal state from hashable object.

        None or no argument seeds from current time or from an operating
        system specific randomness source if available.

        If a is not None or an int or long, hash(a) is used instead.

        a only gets changed at initiation. Counter gets updated each time
        the prng gets called.

        randbits are random bits not yet returned outside the class

        """
        self.baseseed = baseseed
        self.counter = counter
        self.randbits = None
        self.randbits_remaining = 0


    def next(self):
        """
        Update the counter
        """
        self.counter += 1


    def getstate(self):
        return (self.baseseed, self.counter)


    def setstate(self, state):
        """
        Set the state (seed and counter)
        """
        (self.baseseed, self.counter) = (int(val) for val in state)


    def jumpahead(self, n):
        """
        Jump ahead n steps in the period
        """
        self.counter += n


    def __repr__(self):
        """
        >>> r = SHA256(5)
        >>> repr(r)
        'SHA256 PRNG with seed 5'
        >>> str(r)
        'SHA256 PRNG with seed 5'
        """
        stringrepr = self.__class__.__name__ + " PRNG with seed " + \
                    str(self.baseseed) + " and counter " + str(self.counter)
        return stringrepr


################################################################################
############################## SHA-256 Class ###################################
################################################################################

class SHA256(BaseRandom):
    """
    PRNG based on the SHA-256 cryptographic hash function.

    Attributes:
        fill in
    """

    def __init__(self, seed=None):
        """
        Initialize an instance of the SHA-256 PRNG.

        Parameters
        ----------
        seed : {None, int, string} (optional)
        Random seed used to initialize the PRNG. It can be an integer of arbitrary length,
        a string of arbitrary length, or `None`. Default is `None`.
        """
        self.seed(seed)
        self.hashfun = "SHA-256"
        self._basehash()

    def _basehash(self):
        """
        Initialize the SHA256 hash function with given seed
        """
        if self.baseseed is not None:
            hashinput = (str(self.baseseed) + ',').encode()
            self.basehash = hashlib.sha256(hashinput)
        else:
            self.basehash = None


    def seed(self, baseseed=None):
        """
        Initialize internal seed and hashable object with counter 0.

        Parameters
        ----------
        baseseed : {None, int, string} (optional)
            Random seed used to initialize the PRNG. It can be an integer of arbitrary length,
            a string of arbitrary length, or `None`. Default is `None`.
        counter : int (optional)
            Integer that counts how many times the PRNG has been called. The counter
             is used to update the internal state after each step. Default is 0.
        """
        if not hasattr(self, 'baseseed') or baseseed != self.baseseed:
            self.baseseed = baseseed
            self._basehash()
        self.counter = 0
        self.randbits = None
        self.randbits_remaining = 0


    def setstate(self, baseseed=None, counter=0):
        """
        Set the state (seed and counter)

        Parameters
        ----------
        baseseed : {None, int, string} (optional)
            Random seed used to initialize the PRNG. It can be an integer of arbitrary length,
            a string of arbitrary length, or `None`. Default is `None`.
        counter : int (optional)
            Integer that counts how many times the PRNG has been called. The counter
             is used to update the internal state after each step. Default is 0.
        """
        (self.baseseed, self.counter) = (baseseed, counter)
        self._basehash()
        self.basehash.update(b'\x00'*counter)


    def jumpahead(self, n):
        """
        Jump ahead n steps in the period
        """
        self.counter += n
        self.basehash.update(b'\x00'*n)


    def next(self):
        self.jumpahead(1)


    def nextRandom(self):
        """
        Generate the next hash value

        >>> r = SHA256(12345678901234567890)
        >>> r.next()
        >>> expected = int("4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1", 16)
        >>> r.nextRandom() == expected
        True
        """
#        self.basehash.update(bytes(1))
        # Apply SHA-256, interpreting digest output as integer
        # to yield 256-bit integer (a python "long integer")
        hash_output = self.basehash.digest()
        self.next()
        return hash_output


    def random(self, size=None):
        """
        Generate random numbers between 0 and 1.
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.

        >>> r = SHA256(12345678901234567890)
        >>> r.next()
        >>> e1 = int("4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1", 16)
        >>> e2 = int("ae230ec16bee77f77c7378f4eb5d265d931665e29e8bbee7e733f58d3815d338", 16)
        >>> expected = np.array([e1, e2]) * 2**-256
        >>> r.random(2) == expected
        array([ True,  True], dtype=bool)
        """

        if size == None:
            hash_output = self.nextRandom()
            return int_from_hash(hash_output)*RECIP_HASHLEN
        else:
            size2 = np.prod(size)
            hash_output = [self.nextRandom() for i in range(size2)]
            res = int_from_hash(hash_output)*RECIP_HASHLEN
            return np.reshape(res, size)


    def randint_trunc(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.
        """
        assert a <= b, "lower and upper limits are switched"

        if size == None:
            return a + (int_from_hash(self.nextRandom()) % (b-a))
        else:
            return np.reshape(np.array([a + (int_from_hash(self.nextRandom()) % (b-a)) \
                for i in np.arange(np.prod(size))]), size)


    def getrandbits(self, k):
        """
        Returns k pseudorandom bits.

        If self.randbits contains at least k bits, returns k of those bits and removes them.
        If self.randbits has fewer than k bits, calls self.nextRandom() as many times as needed to
        populate self.randbits with at least k random bits, returns those k, and keeps
        any remaining bits in self.randbits
        """
        if self.randbits is None:  # initialize the cache
            self.randbits = int_from_hash(self.nextRandom())
            self.randbits_remaining = HASHLEN
        while k > self.randbits_remaining: # pre-pend more random bits
            # accounts for leading 0s
            self.randbits = (int_from_hash(self.nextRandom()) << \
                                self.randbits_remaining | self.randbits)
            self.randbits_remaining = self.randbits_remaining + HASHLEN
        val = (self.randbits & int(2**k-1)) # harvest least significant k bits
        self.randbits_remaining = self.randbits_remaining - k
        self.randbits = self.randbits >> k # discard the k harvested bits
        return val


    def randbelow_from_randbits(self, n):
        """
        Generate a random integer between 0 (inclusive) and n (exclusive).
        Raises ValueError if n==0.
        """
        k = int(n-1).bit_length()
        r = self.getrandbits(k)   # 0 <= r < 2**k
        while int(r) >= n:
            r = self.getrandbits(k)
        return int(r)


    def randint(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.
        """
        assert a <= b, "lower and upper limits are switched"

        if size == None:
            return a + self.randbelow_from_randbits(b-a)
        else:
            return np.reshape(np.array([a + self.randbelow_from_randbits(b-a) \
                for i in np.arange(np.prod(size))]), size)

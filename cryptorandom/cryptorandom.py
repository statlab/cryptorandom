"""
SHA-256 PRNG prototype in Python
"""

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
############################## SHA-256 Class ###################################
################################################################################

class SHA256(random.Random):
    """
    PRNG based on the SHA-256 cryptographic hash function.
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


    def __repr__(self):
        """
        >>> r = SHA256(5)
        >>> repr(r)
        'SHA256 PRNG. seed: 5 counter: 0 randbits_remaining: 0'
        >>> str(r)
        'SHA256 PRNG. seed: 5 counter: 0 randbits_remaining: 0'
        """
        stringrepr = self.__class__.__name__ + " PRNG. seed: " + \
                    str(self.baseseed) + " counter: " + str(self.counter) + \
                    " randbits_remaining: " + str(self.randbits_remaining)
        return stringrepr


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


    def setstate(self, baseseed=None, counter=0, randbits_remaining=0):
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
        self.randbits_remaining = randbits_remaining


    def getstate(self):
        """
        Get the current state of the PRNG
        """
        return (self.baseseed, self.counter, self.randbits_remaining)


    def jumpahead(self, n):
        """
        Jump ahead n steps in the period

        >>> r = SHA256(5)
        >>> r.jumpahead(5)
        >>> repr(r)
        'SHA256 PRNG with seed 5 and counter 5'
        """
        self.counter += n
        self.basehash.update(b'\x00'*n)


    def next(self):
        """
        Increment the counter and basehash by one
        """
        self.jumpahead(1)


    def nextRandom(self):
        """
        Generate the next hash value

        >>> r = SHA256(12345678901234567890)
        >>> r.next()
        >>> r.nextRandom()
        4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1
        """
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
        >>> r.random(2)
        array([0.9272915426537484, 0.1916135318809483], dtype=object)
        >>> r.random((2, 2))
        array([[0.5846237047310486, 0.18694233108130068],
               [0.9022661737961881, 0.052310932788987144]], dtype=object)

        Parameters
        ----------
        size : {int, tuple, None}
            If None (default), return a single random number.
            If size is an int, return that many random numbers.
            If size is a tuple, it determines the shape of an array
            filled with random numbers.
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
        Deprecated. For large values of (b-a), this algorithm does not produce integers
        uniformly at random.
        
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.

        >>> r = SHA256(12345678901234567890)
        >>> r.randint_trunc(0, 5, size=3)
        array([0, 0, 0])

        Parameters
        ----------
        a : int
            lower limit (included in samples)
        b : int
            upper limit (not included in samples)
        size : {int, tuple, None}
            If None (default), return a single random number.
            If size is an int, return that many random numbers.
            If size is a tuple, it determines the shape of an array
            filled with random numbers.

        """
        assert a <= b, "lower and upper limits are switched"

        if size == None:
            return a + (int_from_hash(self.nextRandom()) % (b-a))
        else:
            return np.reshape(np.array([a + (int_from_hash(self.nextRandom()) % (b-a)) \
                for i in range(np.prod(size))]), size)


    def getrandbits(self, k):
        """
        Generate k pseudorandom bits.

        If self.randbits contains at least k bits, returns k of those bits and removes them.
        If self.randbits has fewer than k bits, calls self.nextRandom() as many times as needed to
        populate self.randbits with at least k random bits, returns those k, and keeps
        any remaining bits in self.randbits

        Parameters
        ----------
        k : int
            number of pseudorandom bits
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

        Parameters
        ----------
        n : int
            upper limit
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

        >>> r = SHA256(12345678901234567890)
        >>> r.randint(0, 5, size=3)
        array([3, 2, 4])

        Parameters
        ----------
        a : int
            lower limit (included in samples)
        b : int
            upper limit (not included in samples)
        size : {int, tuple, None}
            If None (default), return a single random number.
            If size is an int, return that many random numbers.
            If size is a tuple, it determines the shape of an array
            filled with random numbers.
        """
        assert a <= b, "lower and upper limits are switched"

        if size == None:
            return a + self.randbelow_from_randbits(b-a)
        else:
            return np.reshape(np.array([a + self.randbelow_from_randbits(b-a) \
                for i in range(np.prod(size))]), size)

"""
SHA-256 PRNG prototype in Python
"""

from __future__ import division
import numpy as np
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
        stringrepr = self.__class__.__name__ + " PRNG with seed " + str(self.baseseed) + " and counter " + str(self.counter)
        return stringrepr
        
        
################################################################################
############################## SHA-256 Class ###################################
################################################################################

class SHA256(BaseRandom):
    """
    PRNG based on the SHA-256 cryptographic hash function.
    """ 
        
    def random(self, size=None):
        """
        Generate random numbers between 0 and 1.
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.
        """
        if size==None:
            return self.nextRandom()*RECIP_HASHLEN
        else:
            return np.reshape(np.array([self.nextRandom()*RECIP_HASHLEN for i in np.arange(np.prod(size))]), size)

    
    def nextRandom(self):
        """
        Generate the next hash value
        """
        hash_input = (str(self.baseseed) + "," + str(self.counter)).encode('utf-8')
        # Apply SHA-256, interpreting hex output as hexadecimal integer
        # to yield 256-bit integer (a python "long integer")
        hash_output = int(hashlib.sha256(hash_input).hexdigest(),16)
        self.next()
        return(hash_output)
        
    
    def randint_trunc(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.
        """
        assert a <= b, "lower and upper limits are switched"
        
        if size==None:
            return a + (self.nextRandom() % (b-a))
        else:
            return np.reshape(np.array([a + (self.nextRandom() % (b-a)) for i in np.arange(np.prod(size))]), size)
            
            
    def getrandbits(self, k):
        """
        Returns k random bits. 
        If self.randbits contains at least k bits, returns k of those bits and spoils them.
        If self.randbits has fewer than k bits, calls nextRandom as many times as needed to
        be able to return k random bits, and stores the remaining bits in self.randbits
        """
        if randbits is None:                          # initialize the cache
            randbits = self.nextRandom()
            randbits_remaining = HASHLEN
        while k > randbits_remaining:                 # pre-pend more random bits
            randbits = (self.nextRandom() << randbits_remaining | randbits )  # accounts for leading 0s
            randbits_remaining = randbits_remaining + HASHLEN
        val = (randbits & int(2**(k+1)-1))            # harvest least significant k bits
        randbits_remaining = randbits_remaining - k
        randbits = randbits >> k                      # discard the k harvested bits
        return val
        
    def randbelow_from_randbits(self, n):
        """
        Generate a random integer between 0 (inclusive) and n (exclusive).
        Raises ValueError if n==0.
        """
        mu = int(n).bit_length()
        r = self.getrandbits(mu) # 0 <= r < 2**mu
        while r >= n:
            r = self.getrandbits(mu)
        return r
        
        
    def randint(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.
        """
        assert a <= b, "lower and upper limits are switched"
        
        if size==None:
            return a + self.randbelow_from_randbits(b-a)
        else:
            return np.reshape(np.array([a + self.randbelow_from_randbits(b-a) for i in np.arange(np.prod(size))]), size)
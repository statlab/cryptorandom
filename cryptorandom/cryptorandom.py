"""
To run docstring tests, run the following from the terminal:

python sha256prng.py -v
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
        """
        self.baseseed = baseseed
        self.counter = counter

        
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
        stringrepr = self.__class__.__name__ + " PRNG with seed " + str(self.baseseed)
        return stringrepr
        
        
################################################################################
############################## SHA-256 Class ###################################
################################################################################

class SHA256(BaseRandom):
    """
    PRNG based on the SHA-256 cryptographic hash function.
    
    >>> r = SHA256(5)
    >>> r.getstate()
    (5, 0)
    >>> r.next()
    >>> r.getstate()
    (5, 1)
    >>> r.jumpahead(5)
    >>> r.getstate()
    (5, 6)
    >>> r.seed(22, 3)
    >>> r.getstate()
    (22, 3)
    """
    
#    def __init__(self, seed=None):
#        self.__init__(seed=seed)
#        self.hashfun = "SHA-256"
        
        
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
        if size==None:
            return self.nextRandom()*RECIP_HASHLEN
        else:
            return np.reshape(np.array([self.nextRandom()*RECIP_HASHLEN for i in np.arange(np.prod(size))]), size)
            
    
    def nextRandom(self):
        """
        Generate the next hash value
        
        >>> r = SHA256(12345678901234567890)
        >>> r.next()
        >>> expected = int("4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1", 16)
        >>> r.nextRandom() == expected
        True
        """
        hash_input = (str(self.baseseed) + "," + str(self.counter)).encode('utf-8')
        # Apply SHA-256, interpreting hex output as hexadecimal integer
        # to yield 256-bit integer (a python "long integer")
        hash_output = int(hashlib.sha256(hash_input).hexdigest(),16)
        self.next()
        return(hash_output)
        
    
    def randint(self, a, b, size=None):
        """
        Generate random integers between a and b, inclusive.
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.

        >>> r = SHA256(12345678901234567890)
        >>> r.randint(1, 1000, 5)
        array([405, 426, 921, 929,  56])
        """
        assert a <= b, "lower and upper limits are switched"
        
        if size==None:
            return a + (self.nextRandom() % (b-a+1))
        else:
            return np.reshape(np.array([a + (self.nextRandom() % (b-a+1)) for i in np.arange(np.prod(size))]), size)

        
        
################################################################################
############################## some sample code ################################
################################################################################

# pseudo-random number generator
def toy_example():
    seed = 12345678901234567890
    count = 0
    hash_input = (str(seed) + "," + str(count)).encode('utf-8')
    # Apply SHA-256, interpreting hex output as hexadecimal integer
    # to yield 256-bit integer (a python "long integer")
    hash_output = int(hashlib.sha256(hash_input).hexdigest(),16)

    print(hash_output*RECIP_HASHLEN)
    count += 1


if __name__ == "__main__":
    import doctest
    doctest.testmod()
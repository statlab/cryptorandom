from __future__ import division
import numpy as np

# LCG; defaults to RANDU, a particularly bad choice
class lcgRandom: # defaults to RANDU: BEWARE!
    def __init__(self, seed=1234567890, A=0, B=65539, M = 2**31): 
        self.state = seed
        self.A = A
        self.B = B
        self.M = M
        
    def getState(self):
        return self.state, self.A, self.B, self.M
    
    def setState(self,seed=1234567890, A=0, B=65539, M = 2**31):
        self.state = seed
        self.A = A
        self.B = B
        self.M = M

    def nextRandom(self):
        self.state = (self.A + self.B * self.state) % self.M
        return self.state/self.M

    def random(self, size=None):  # vector of rands
        if size==None:
            return self.nextRandom()
        else: 
            return np.reshape(np.array([self.nextRandom() for i in np.arange(np.prod(size))]), size)
    
    def randint(self, low=0, high=None, size=None):  # integer between low (inclusive) and high (exclusive)
        if high==None:  # numpy.random.randint()-like behavior
            high, low = low, 0
        if size==None:
            return low + np.floor(self.nextRandom()*(high-low)) # NOT AN ACCURATE ALGORITHM! See below.
        else:
            return low + np.floor(self.random(size=size)*(high-low))
            

# Python implementation of MT19937 from Wikipedia 
# https://en.wikipedia.org/wiki/Mersenne_Twister#Python_implementation
# We changed what used to be called "extract_number" to "nextRandom",
# and "random", to follow convention of other Python PRNGs

def _int32(x):
    # Get the 32 least significant bits.
    return int(0xFFFFFFFF & x)


class MT19937:

    def __init__(self, seed):
        # Initialize the index to 0
        self.index = 624
        self.mt = [0] * 624
        self.mt[0] = seed  # Initialize the initial state to the seed
        for i in range(1, 624):
            self.mt[i] = _int32(
                1812433253 * (self.mt[i - 1] ^ self.mt[i - 1] >> 30) + i)

    def random(self, size=None):  # vector of rands
        if size==None:
            return self.nextRandom()
        else: 
            return np.reshape(np.array([self.nextRandom() for i in np.arange(np.prod(size))]), size)
    
    def nextRandom(self): 
        if self.index >= 624:
            self.twist()

        y = self.mt[self.index]

        # Right shift by 11 bits
        y = y ^ y >> 11
        # Shift y left by 7 and take the bitwise and of 2636928640
        y = y ^ y << 7 & 2636928640
        # Shift y left by 15 and take the bitwise and of y and 4022730752
        y = y ^ y << 15 & 4022730752
        # Right shift by 18 bits
        y = y ^ y >> 18

        self.index = self.index + 1

        return _int32(y)

    def twist(self):
        for i in range(624):
            # Get the most significant bit and add it to the less significant
            # bits of the next number
            y = _int32((self.mt[i] & 0x80000000) +
                       (self.mt[(i + 1) % 624] & 0x7fffffff))
            self.mt[i] = self.mt[(i + 397) % 624] ^ y >> 1

            if y % 2 != 0:
                self.mt[i] = self.mt[i] ^ 0x9908b0df
        self.index = 0
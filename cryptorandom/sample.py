from __future__ import division
import numpy as np
#cimport numpy as np
#import cython

def randomSample(n, N, weights=None, replace=False, method="Cormen", prng=np.random)
    '''
       Random sample of size n from a population of size N drawn with or without weights, with or without replacement.
       
       If no weights are provided, the sample is drawn with equal probability of selecting every item.
       If weights are provided, len(weights) must equal N.
       
       Sampling methods available are 
           Fisher-Yates:    sampling without weights, without replacement
           PIKK:            sampling without weights, without replacement (deprecated)
           Cormen:          samping without weights, without replacement
           Waterman_R:      sampling without weights, without replacement
           Vitter_Z:        sampling without weights, without replacement
           sample_by_index: sampling without weights, without replacement
           
           Exponential:     sampling with weights, without replacement (deprecated)
           Elimination:     sampling with weights, without replacement
           ...
    '''
    if weights is not None:
        assert len(weights) == N
    if not replace:
        assert n <= N
        
    methods = {
        "Fisher-Yates" : lambda  N, n: fykd(N, n, gen=prng),
        "PIKK" : lambda N, n: PIKK(N, n, gen=prng),
        "Cormen" : lambda N, n: Random_Sample(N, n, gen=prng),
        "Waterman_R" : lambda N, n: Algorithm_R(N, n, gen=prng),
        "Vitter_Z" :  # TODO
        "sample_by_index" : lambda N, n: sample_by_index(N, n, gen=prng)
        "Exponential" : lambda N, n: exponential_sample(n, weights, prng),
        "Elimination" : lambda N, n: elimination_sample(n, weights, replace, prng)
    }
    
    try: 
        sam = methods[method](N, n):
    except ValueError: 
        print("Sampling method is incompatible with the inputs")
    return sam
    
    
###################### Sampling functions #####################################

def fykd_sample(n, k, gen=np.random):
    '''
    Use fykd to sample k out of 1, ..., n
    '''
    a = list(range(1, n+1))
    rand = gen.random(k)
    ind = np.array(range(k))
    JJ = np.array(ind + rand*(n - ind), dtype = int)
    for i in range(k):
        J = JJ[i]
        a[i], a[J] = a[J], a[i]
    return(a[:k])


def PIKK(n, k, gen=np.random):
    '''
    PIKK Algorithm: permute indices and keep k
    '''
    return set(np.argsort(gen.random(n))[0:k])


def Random_Sample(n, k, gen=np.random):
    '''
    Recursive sampling algorithm from Cormen et al
    '''
    if k==0:
        return set()
    else:
        S = Random_Sample(n-1, k-1)
        i = gen.randint(1,n+1) 
        if i in S:
            S = S.union([n])
        else:
            S = S.union([i])
    return S


def Algorithm_R(n, k, gen=np.random):  
    '''
    Waterman's Algorithm R for resevoir SRSs
    '''
    S = list(range(1, k+1))  # fill the reservoir
    for t in range(k+1,n+1):
        i = gen.randint(1,t+1)
        if i <= k:
            S[i-1] = t
    return set(S)


def sample_by_index(int n, int k, gen=np.random):
    '''
    Generate a random sample of 1,...,n by selecting indices uniformly at random
    '''
    cdef int nprime = n
    cdef int j, w
    S = set()
    Pop = list(range(1, n+1))
    while nprime > n-k:
        w = gen.randint(1, nprime+1)
        j = Pop[w-1]
        S = S.union([j])
        lastvalue = Pop.pop()
        if w < nprime:
            Pop[w-1] = lastvalue # Move last population item to the wth position
        nprime = nprime - 1
    return set(S)
    
    
def elimination_sample(n, weights, replace=True, prng=np.random):
    '''
       Weighted random sample of size n drawn with or without replacement.
       The algorithm is inefficient but transparent.
       
       Walker's alias method is more efficient.
    '''
    if any(weights < 0):
        raise ValueError('negative item weight')
    else:
        weights = np.array(weights).astype(float) # ensure the weights are floats
        if replace:
            wc = np.cumsum(weights)/np.sum(weights)  # normalize the weights
            theSam = prng.random(size=n)             # generate n IID U[0,1] variables
            return(wc.searchsorted(theSam))
        else:
            if n > len(weights):
                raise ValueError('sample size larger than population in sample without replacement')
            elif n == len(weights):
                return(np.array(range(n)))
            else:
                weights_left = np.copy(weights)           # remaining weights
                indices_left = list(range(len(weights)))  # remaining indices
                theSam = np.full(n, -1)
                for i in range(n):
                    wc = np.cumsum(weights_left)/np.sum(weights_left) # normalize remaining weights
                    v = prng.random()              # generate a U[0,1]
                    inx = wc.searchsorted(v)       # draw one item with probability proportional to the weight
                    theSam[i] = indices_left[inx]  # add the item to the sample
                    indices_left = np.delete(indices_left, inx)   # delete the index 
                    weights_left = np.delete(weights_left, inx)   # delete the corresponding weight
                return(theSam)


def exponential_sample(n, weights, prng=np.random):
    '''
       Weighted random sample of size n without replacement.
       
       Let X_1, ..., X_N be independent exponential random variables with rates w_1, ..., w_N,
       and let W = w_1 + ... + w_N.
       
       Then the chance that X_k is the smallest of them is w_k/W.
       
       Because of the "memoryless" property of exponential random variables and the independence, if
       the smallest is removed, for j!=k, the chance that X_j is the smallest of the remaining variables
       is w_j/(W-w_k), and so on.
       
       The percentile function of the exponential distribution with rate w is -ln(1-F)/w.
       
       Hence, if U~U[0,1], -ln(U)/w ~ exp(w).
              
    '''
    if any(weights < 0):
        raise ValueError('negative item weight')
    else:
        theSam = prng.random(size=len(weights))
        theSam = -np.log(theSam)/weights
        sample = theSam.argsort()[0:n]
        return(sample)


########################### cython functions ###################################

"""

def fykd_sample_c(int n, int k, gen=np.random):
    '''
    Use fykd to sample k out of 1, ..., n
    '''
    cdef int i, J
    cdef np.ndarray[np.int64_t] a = np.array(range(1, n+1), dtype=np.int64)
    cdef np.ndarray[double] rand = gen.random(k)
    cdef np.ndarray[np.int64_t] ind = np.array(range(k), dtype=np.int64)
    JJ = np.array(ind + rand*(n - ind), dtype = int)
    for i in range(k):
        J = JJ[i]
        a[i], a[J] = a[J], a[i]
    return(a[:k])


def Random_Sample_c(int n, int k, gen=np.random):
    '''
    Recursive sampling algorithm from Cormen et al
    '''
    cdef int i
    if k==0:
        return set()
    else:
        S = Random_Sample(n-1, k-1, gen=gen)
        i = gen.randint(1,n+1) 
        if i in S:
            S = S.union([n])
        else:
            S = S.union([i])
    return S    


def Algorithm_R_c(int n, int k, gen=np.random):  
    '''
    Waterman's Algorithm R for resevoir SRSs
    '''
    cdef int t
    S = list(range(1, k+1))  # fill the reservoir
    for t in range(k+1,n+1):
        i = gen.randint(1,t+1)
        if i <= k:
            S[i-1] = t
    return set(S)


def sample_by_index_c(int n, int k, gen=np.random):
    '''
    Generate a random sample of 1,...,n by selecting indices uniformly at random
    '''
    cdef int nprime = n
    cdef int j, w
    S = set()
    Pop = list(range(1, n+1))
    while nprime > n-k:
        w = gen.randint(1, nprime+1)
        j = Pop[w-1]
        S = S.union([j])
        lastvalue = Pop.pop()
        if w < nprime:
            Pop[w-1] = lastvalue # Move last population item to the wth position
        nprime = nprime - 1
    return set(S)
	
"""
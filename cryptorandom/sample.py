from __future__ import division
import numpy as np
import math

def randomSample(a, size, replace=False, p=None, method="sample_by_index", prng=np.random):
    '''
    Random sample of size `size` from a population `a` drawn with or without weights,
    with or without replacement.

    If no weights are provided, the sample is drawn with equal probability of selecting every item.
    If weights are provided, len(weights) must equal N.

    Sampling methods available are:
        Fisher-Yates:    sampling without weights, without replacement
        PIKK:            sampling without weights, without replacement (deprecated)
        Cormen:          samping without weights, without replacement
        Waterman_R:      sampling without weights, without replacement
        Vitter_Z:        sampling without weights, without replacement
        sample_by_index: sampling without weights, without replacement

        Exponential:     sampling with weights, without replacement (deprecated)
        Elimination:     sampling with weights, without replacement
        ...

    Parameters
    ----------
    a : 1-D array-like or int
        If an array or list, a random sample is generated from its elements.
        If an int, the random sample is generated as if a were np.arange(a)
    size : int or tuple of ints, optional
        Output shape. If the given shape is, e.g., (m, n, k),
        then m * n * k samples are drawn.
        Default is None, in which case a single value is returned.
    replace : boolean, optional
        Whether the sample is with or without replacement.
        Default False.
    p : 1-D array-like, optional
        The probabilities associated with each entry in a.
        If not given the sample assumes a uniform distribution over all entries in a.
    method : string
        Which sampling function?
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    samples : single item or ndarray
        The generated random samples
    '''
    if isinstance(a, (list, np.ndarray)):
        N = len(a)
    elif isinstance(a, int):
        N = a
        a = np.arange(N)
        assert N > 0, "Population size must be nonnegative"
    else:
        raise ValueError("a must be an integer or array-like")

    if p is not None:
        assert len(p) == N
    if not replace:
        assert size <= N

    methods = {
        "Fisher-Yates" : lambda  N, n: fykd_sample(N, n, gen=prng),
        "PIKK" : lambda N, n: PIKK(N, n, gen=prng),
        "Cormen" : lambda N, n: Random_Sample(N, n, gen=prng),
        "Waterman_R" : lambda N, n: Algorithm_R(N, n, gen=prng),
        "Vitter_Z" : lambda N, n: Algorithm_Z(N, n, gen=prng),
        "sample_by_index" : lambda N, n: sample_by_index(N, n, gen=prng),
        "Exponential" : lambda N, n: exponential_sample(n, p, prng),
        "Elimination" : lambda N, n: elimination_sample(n, p, replace, prng)
    }

    try:
        sam = np.array(methods[method](N, size)) - 1 # shift to 0 indexing
    except ValueError:
        print("Sampling method is incompatible with the inputs")
    return a[sam]


###################### Sampling functions #####################################

def fykd_sample(n, k, gen=np.random):
    '''
    Use fykd to sample k out of 1, ..., n
    '''
    a = list(range(1, n+1))
    rand = gen.random(k)
    ind = np.array(range(k))
    JJ = np.array(ind + rand*(n - ind), dtype=int)
    for i in range(k):
        J = JJ[i]
        a[i], a[J] = a[J], a[i]
    return a[:k]


def PIKK(n, k, gen=np.random):
    '''
    PIKK Algorithm: permute indices and keep k.
    Contrary to what Python does, this assumes indexing starts at 1.
    '''
    return np.argsort(gen.random(n))[0:k] + 1


def Random_Sample(n, k, gen=np.random):
    '''
    Recursive sampling algorithm from Cormen et al
    Draw a sample of k out of 1, ..., n.
    '''
    if k == 0:
        return []
    else:
        S = Random_Sample(n-1, k-1, gen=gen)
        i = gen.randint(1, n+1)
        if i in S:
            S.append(n)
        else:
            S.append(i)
    return S


def Algorithm_R(n, k, gen=np.random):
    '''
    Waterman's Algorithm R for resevoir SRSs
    Draw a sample of k out of 1, ..., n.
    '''
    S = list(range(1, k+1))  # fill the reservoir
    for t in range(k+1, n+1):
        i = gen.randint(1, t+1)
        if i <= k:
            S[i-1] = t
    return S


def Algorithm_Z(n, k, gen=np.random):
    
    def Algorithm_X(n, t):
        V = gen.random()
        s = 0
        frac = 2
        while frac > V:
            s += 1
            frac = ((t+1-n)/(t+1))**(s+1)
        return s

    def f(x, t):
        numer = math.factorial(t-k+x)/math.factorial(t-k-1)
        denom = math.factorial(t+x+1)/math.factorial(t)
        return numer/denom * k/(t-k)
    
    def g(x, t):
        assert x>=0
        return k/(t+x) * (t/(t+x))**k
        
    def h(x, t):
        assert x>=0
        return k/(t+1) * ((t-k+1)/(t+x-k+1))**(k+1)

    def c(t):
        return (t+1)/(t-k+1)

    sam = list(range(1, k+1))  # fill the reservoir
    t = k
    
    while t<=n:
        # Determine how many unseen records, nu, to skip
        if t <= 22*k: # the choice of 22 is taken from Vitter's 1985 ACM paper
            nu = Algorithm_X(k, t)
        else:
            var = -2
            U = 2
            while U > var:
                V = gen.random()
                X = t*(V**(-1/k) - 1)
                U = gen.random()
                if U <= h(np.floor(X), t)/(c(t)*g(X, t)):
                    break
                var = f(np.floor(X), t)/(c(t)*g(X, t))
            nu = np.floor(X)
        if t+nu <= n:
            # Make the next record a candidate, replacing one at random
            i = gen.randint(0, k)
            sam[i] = int(t+nu)
        t = t+nu+1
    return sam


def sample_by_index(n, k, gen=np.random):
    '''
    Generate a random sample of 1,...,n by selecting indices uniformly at random
    '''
    nprime = n
    S = []
    Pop = list(range(1, n+1))
    while nprime > n-k:
        w = gen.randint(1, nprime+1)
        j = Pop[w-1]
        S.append(j)
        lastvalue = Pop.pop()
        if w < nprime:
            Pop[w-1] = lastvalue # Move last population item to the wth position
        nprime = nprime - 1
    return S


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
            return wc.searchsorted(theSam)
        else:
            if n > len(weights):
                raise ValueError('sample size larger than population in sample without replacement')
            elif n == len(weights):
                return np.array(range(n))
            else:
                weights_left = np.copy(weights)           # remaining weights
                indices_left = list(range(len(weights)))  # remaining indices
                theSam = np.full(n, -1)
                for i in range(n):
                    # normalize remaining weights
                    wc = np.cumsum(weights_left)/np.sum(weights_left)
                    # generate a U[0,1]
                    v = prng.random()
                    # draw one item with probability proportional to the weight
                    inx = wc.searchsorted(v)
                    # add the item to the sample
                    theSam[i] = indices_left[inx]
                    # delete the index
                    indices_left = np.delete(indices_left, inx)
                    # delete the corresponding weight
                    weights_left = np.delete(weights_left, inx)
                return theSam


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
        return sample

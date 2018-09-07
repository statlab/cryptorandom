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
        "Fisher-Yates" : lambda  N, n: fykd_sample(N, n, prng=prng),
        "PIKK" : lambda N, n: PIKK(N, n, prng=prng),
        "Cormen" : lambda N, n: Random_Sample(N, n, prng=prng),
        "Waterman_R" : lambda N, n: Algorithm_R(N, n, prng=prng),
        "Vitter_Z" : lambda N, n: Algorithm_Z(N, n, prng=prng),
        "sample_by_index" : lambda N, n: sample_by_index(N, n, prng=prng),
        "Exponential" : lambda N, n: exponential_sample(n, p, prng),
        "Elimination" : lambda N, n: elimination_sample(n, p, replace, prng)
    }

    try:
        sam = np.array(methods[method](N, size)) - 1 # shift to 0 indexing
    except ValueError:
        print("Sampling method is incompatible with the inputs")
    return a[sam]


###################### Sampling functions #####################################

def fykd_sample(n, k, prng=np.random):
    '''
    Use fykd to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    a = list(range(1, n+1))
    rand = prng.random(k)
    ind = np.array(range(k))
    JJ = np.array(ind + rand*(n - ind), dtype=int)
    for i in range(k):
        J = JJ[i]
        a[i], a[J] = a[J], a[i]
    return a[:k]


def PIKK(n, k, prng=np.random):
    '''
    PIKK Algorithm: permute indices and keep k to draw a sample
    from 1, ..., n without replacement.
    Contrary to what Python does, this assumes indexing starts at 1.

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    return np.argsort(prng.random(n))[0:k] + 1


def Random_Sample(n, k, prng=np.random):
    '''
    Recursive sampling algorithm from Cormen et al
    Draw a sample of to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    if k == 0:
        return []
    else:
        S = Random_Sample(n-1, k-1, prng=prng)
        i = prng.randint(1, n+1)
        if i in S:
            S.append(n)
        else:
            S.append(i)
    return S


def Algorithm_R(n, k, prng=np.random):
    '''
    Waterman's Algorithm R for resevoir SRSs
    Draw a sample of to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    S = list(range(1, k+1))  # fill the reservoir
    for t in range(k+1, n+1):
        i = prng.randint(1, t+1)
        if i <= k:
            S[i-1] = t
    return S


def Algorithm_Z(n, k, prng=np.random):
    '''
    Vitter's Algorithm Z for resevoir SRSs (Vitter 1985).
    Draw a sample of to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    def Algorithm_X(n, t):
        V = prng.random()
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
                V = prng.random()
                X = t*(V**(-1/k) - 1)
                U = prng.random()
                if U <= h(np.floor(X), t)/(c(t)*g(X, t)):
                    break
                var = f(np.floor(X), t)/(c(t)*g(X, t))
            nu = np.floor(X)
        if t+nu <= n:
            # Make the next record a candidate, replacing one at random
            i = prng.randint(0, k)
            sam[i] = int(t+nu)
        t = t+nu+1
    return sam


def sample_by_index(n, k, prng=np.random):
    '''
    Select indices uniformly at random to
    draw a sample of to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    nprime = n
    S = []
    Pop = list(range(1, n+1))
    while nprime > n-k:
        w = prng.randint(1, nprime+1)
        j = Pop[w-1]
        S.append(j)
        lastvalue = Pop.pop()
        if w < nprime:
            Pop[w-1] = lastvalue # Move last population item to the wth position
        nprime = nprime - 1
    return S


def elimination_sample(k, p, replace=True, prng=np.random):
    '''
    Weighted random sample of size n drawn with or without replacement.
    The algorithm is inefficient but transparent.
    Walker's alias method is more efficient.

    Parameters
    ----------
    k : int
        Desired sample size
    p : 1-D array-like, optional
        The probabilities associated with each value in 1, ... n.
    replace : boolean, optional
        Whether the sample is with or without replacement.
        Default True.
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    weights = np.array(p).astype(float) # ensure the weights are floats
    if any(weights < 0):
        raise ValueError('negative item weight')
    else:
        n = len(weights)
        if replace:
            wc = np.cumsum(weights)/np.sum(weights)  # normalize the weights
            sam = prng.random(size=k)
            return wc.searchsorted(sam)
        else:
            if k > n:
                raise ValueError('sample size larger than population in \
                    sample without replacement')
            elif k == n:
                return np.array(range(k))
            else:
                weights_left = np.copy(weights)
                indices_left = list(range(n))
                sam = np.full(n, -1)
                for i in range(n):
                    # normalize remaining weights
                    wc = np.cumsum(weights_left)/np.sum(weights_left)
                    # generate a U[0,1]
                    v = prng.random()
                    # draw one item with probability proportional to the weight
                    inx = wc.searchsorted(v)
                    # add the item to the sample
                    sam[i] = indices_left[inx]
                    # delete the index
                    indices_left = np.delete(indices_left, inx)
                    # delete the corresponding weight
                    weights_left = np.delete(weights_left, inx)
                return sam


def exponential_sample(k, p, prng=np.random):
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

    Parameters
    ----------
    k : int
        Desired sample size
    p : 1-D array-like, optional
        The probabilities associated with each value in 1, ... n.
    prng : object
        Instance of a pseudo-random number generator, already seeded.
        Default is Numpy PRNG (Mersenne Twister)
    Returns
    -------
    list of items sampled
    '''
    weights = np.array(p).astype(float) # ensure the weights are floats
    if any(weights < 0):
        raise ValueError('negative item weight')
    n = len(weights)
    if k > n:
        raise ValueError('sample size larger than population in \
            sample without replacement')
    elif k == n:
        return np.array(range(k))
    else:
        sam = prng.random(size=n)
        sam = -np.log(sam)/weights
        sample = sam.argsort()[0:k]
        return sample

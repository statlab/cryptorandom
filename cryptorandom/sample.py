"""
Sampling with or without weights, with or without replacement.
"""

import numpy as np
import math
from .cryptorandom import SHA256

def get_prng(seed=None):
    """Turn seed into a PRNG instance

    Parameters
    ----------
    seed : {None, int, object}
        If seed is None, return a randomly seeded instance of SHA256.
        If seed is an int, return a new SHA256 instance seeded with seed.
        If seed is already a PRNG instance, return it.
        Otherwise raise ValueError.

    Returns
    -------
    object
    """
    if seed is None:
        seed = np.random.randint(0, 10**10, dtype=np.int64) # generate an integer
        return SHA256(seed)
    if isinstance(seed, (int, np.integer)):
        return SHA256(seed)
    if hasattr(seed, "random") and hasattr(seed, "randint"):
        return seed
    raise ValueError(f'{seed!r} cannot be used to seed a PRNG')


def random_sample(a, size, replace=False, fast=False, p=None, method="sample_by_index", prng=None):
    '''
    Random sample of size `size` from a population `a` drawn with or without weights,
    with or without replacement.

    If no weights are provided, the sample is drawn with equal probability of selecting every item.
    If weights are provided, len(weights) must equal N.

    Sampling methods available are:
        * Fisher-Yates:    sampling without weights, without replacement
        * PIKK:            sampling without weights, without replacement
        * recursive:       samping without weights, without replacement
        * Waterman_R:      sampling without weights, without replacement
        * Vitter_Z:        sampling without weights, without replacement
        * sample_by_index: sampling without weights, without replacement
        * Exponential:     sampling with weights, without replacement
        * Elimination:     sampling with weights, without replacement
    
    Fisher-Yates, PIKK, sample_by_index, Exponential, and Elimination return ordered samples, 
    i.e. they are equally likely to return [1, 2] as they are to return [2, 1]. Waterman_R,
    Vitter_Z, and recursive aren't guaranteed to randomize the order of items in the sample.
    
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
    fast : boolean, optional
        Whether to speed up sampling by not sampling with random order.
        Default False.
    p : 1-D array-like, optional
        The probabilities associated with each entry in a.
        If not given the sample assumes a uniform distribution over all entries in a.
    method : string
        Which sampling function?
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    samples : single item or ndarray
        The generated random samples
    '''
    prng = get_prng(prng)
    if isinstance(a, (list, np.ndarray)):
        N = len(a)
        a = np.array(a)
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
        "PIKK" : lambda N, n: pikk(N, n, prng=prng),
        "recursive" : lambda N, n: recursive_sample(N, n, prng=prng),
        "Waterman_R" : lambda N, n: waterman_r(N, n, prng=prng),
        "Vitter_Z" : lambda N, n: vitter_z(N, n, prng=prng),
        "sample_by_index" : lambda N, n: sample_by_index(N, n, replace=replace, fast=fast, prng=prng),
        "Exponential" : lambda n, p: exponential_sample(n, p, prng=prng),
        "Elimination" : lambda n, p: elimination_sample(n, p, replace=replace, prng=prng)
    }

    if replace is False and p is None:
        try:
            sam = np.array(methods[method](N, size), dtype=np.int64) - 1 # shift to 0 indexing
        except ValueError:
            print("Sampling method is incompatible with the inputs")
    elif replace is True and method in ['Fisher-Yates', 'PIKK', 'recursive',
        'Waterman_R', 'Vitter_Z']:
        raise ValueError("Method is meant for sampling without replacement")
    elif replace is True and method in ['sample_by_index']:
        try:
            sam = np.array(methods[method](N, size), dtype=np.int64) - 1 # shift to 0 indexing
        except ValueError:
            print("Sampling method is incompatible with the inputs")
    else:
        try:
            sam = np.array(methods[method](size, p), dtype=np.int64) - 1
        except ValueError:
            print("Sampling method is incompatible with the inputs")
    return a[sam]


def random_allocation(a, sizes, replace=False, fast=False, p=None, method="sample_by_index", prng=None):
    '''
    Random samples of sizes `sizes` from a population `a` drawn with or without replacement.
    
    Parameters
    ----------
    a : 1-D array-like or int
        If an array or list, a random sample is generated from its elements.
        If an int, the random sample is generated as if a were np.arange(a)
    sizes : 1-D array-like
        sizes of samples to return
    replace : boolean, optional
        Whether the sampling is with or without replacement.
        Default False.
    fast : boolean, optional
        Whether to speed up sampling by not sampling with random order.
        Default False.
    p : 1-D array-like, optional
        The probabilities associated with each entry in a.
        If not given the sample assumes a uniform distribution over all entries in a.
    method : string
        Which sampling function? 
        Default sample_by_index
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    samples : list of lists
        The generated random samples
    '''
    if isinstance(a, (list, np.ndarray)):
        N = len(a)
        a = np.array(a)
        indices = np.arange(N)
    elif isinstance(a, int):
        N = a
        a = np.arange(N)
        indices = np.arange(N)
        assert N > 0, "Population size must be nonnegative"
        
    # raise error if without replacement and sample sizes greater than population size
    if not replace and np.sum(sizes) > N:
        raise ValueError('sample sizes greater than population size')
        
    samples = [0] * len(sizes)
    # sort sizes from smallest to largest
    sizes.sort()
    # get random samples for all the groups except the largest one
    for i in range(len(sizes) - 1):
        sam = random_sample(list(indices), sizes[i], replace, fast, p, method, prng)
        samples[i] = a[sam]
        if not replace:
            indices = set(indices) - set(sam)
    # get the sample for the largest group
    if not replace and N == np.sum(sizes):
        sam = list(indices)
    else:
        sam = random_sample(list(indices), sizes[-1], replace, fast, p, method, prng)
    samples[-1] = a[sam]
    
    return samples
            

def random_permutation(a, method="Fisher-Yates", prng=None):
    '''
    Construct a random permutation (re-ordering) of a population `a`.
    
    The algorithms available are:
        * Fisher-Yates:        a shuffling algorithm
        * random_sort:         generate random floats and sort
        * permute_by_index:    sample integer indices without replacement

    Parameters
    ----------
    a : 1-D array-like or int
        If an array or list, a random permutation is generated from its elements.
        If an int, the random permutation is generated as if a were np.arange(a)
    method : string
        Which sampling function?
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    samples : single item or ndarray
        The generated random samples
    '''
    prng = get_prng(prng)
    if isinstance(a, (list, np.ndarray)):
        N = len(a)
        a = np.array(a)
    elif isinstance(a, int):
        N = a
        a = np.arange(N)
        assert N > 0, "Population size must be nonnegative"
    else:
        raise ValueError("a must be an integer or array-like")

    methods = {
        "Fisher-Yates" : lambda  N: fykd_sample(N, N, prng=prng),
        "random_sort" : lambda N: pikk(N, N, prng=prng),
        "permute_by_index" : lambda N: sample_by_index(N, N, prng=prng),
    }

    try:
        sam = np.array(methods[method](N), dtype=np.int64) - 1 # shift to 0 indexing
    except ValueError:
        print("Bad permutation algorithm")
    return a[sam]


###################### Sampling functions #####################################

def fykd_sample(n, k, prng=None):
    '''
    Use fykd to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled
    '''
    prng = get_prng(prng)
    a = np.array(range(1, n+1))
    rand = prng.random(k)
    ind = np.array(range(k))
    JJ = np.array(ind + rand*(n - ind), dtype=int)
    for i in range(k):
        J = JJ[i]
        a[i], a[J] = a[J], a[i]
    return a[:k]


def pikk(n, k, prng=None):
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
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled
    '''
    prng = get_prng(prng)
    return np.argsort(prng.random(n))[0:k] + 1


def recursive_sample(n, k, prng=None):
    '''
    Recursive sampling algorithm from Cormen et al
    Draw a sample of to sample k out of 1, ..., n without replacement

    Note that if k is larger than the default recursion limit of 1000, 
    this function will throw an error. You can change the recursion
    depth using `sys.setrecursionlimit()`.

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled
    '''
    prng = get_prng(prng)
    if k == 0:
        return np.empty(0, dtype=np.int64)
    else:
        S = recursive_sample(n-1, k-1, prng=prng)
        i = prng.randint(1, n+1)
        if i in S:
            S = np.append(S, [n])
        else:
            S = np.append(S, [i])
    return S


def waterman_r(n, k, prng=None):
    '''
    Waterman's Algorithm R for reservoir SRSs
    Draw a sample of to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled
    '''
    prng = get_prng(prng)
    S = np.array(range(1, k+1))  # fill the reservoir
    for t in range(k+1, n+1):
        i = prng.randint(1, t+1)
        if i <= k:
            S[i-1] = t
    return S


def vitter_z(n, k, prng=None):
    '''
    Vitter's Algorithm Z for reservoir SRSs (Vitter 1985).
    Draw a sample of to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled
    '''
    prng = get_prng(prng)
    
    def Algorithm_X(n, t):
        V = prng.random()
        s = 0
        numer = math.factorial(t+s+1-n)/math.factorial(t-n)
        denom = math.factorial(t+s+1)/math.factorial(t)
        frac = numer/denom
        
        while frac > V:
            s += 1
            numer = (t+s+1-n)*numer
            denom = (t+s+1)*denom
            frac = numer/denom
        return s

    def f(x, t):
        numer = math.factorial(t-k+x)/math.factorial(t-k-1)
        denom = math.factorial(t+x+1)/math.factorial(t)
        return numer/denom * k/(t-k)

    def g(x, t):
        assert x >= 0
        return k/(t+x) * (t/(t+x))**k

    def h(x, t):
        assert x >= 0
        return k/(t+1) * ((t-k+1)/(t+x-k+1))**(k+1)

    def c(t):
        return (t+1)/(t-k+1)

    sam = np.array(range(1, k+1))  # fill the reservoir
    t = k

    while t < n:
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
        if t+nu < n:
            # Make the next record a candidate, replacing one at random
            i = prng.randint(0, k)
            sam[i] = int(t+nu+1)
        t = t+nu+1
    return sam


def sample_by_index(n, k, replace=False, fast=False, prng=None):
    '''
    Select indices uniformly at random to
    draw a sample of to sample k out of 1, ..., n without replacement

    Parameters
    ----------
    n : int
        Population size
    k : int
        Desired sample size
    replace : boolean, optional
        Whether the sample is with or without replacement.
        Default False.
    fast : boolean, optional
        Whether to speed up sampling by not sampling with random order.
        Default False.
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled, in random order if not fast
    '''
    # raise error if without replacement and sample size greater than population size
    if not replace and k > n:
        raise ValueError('sample size greater than population size')
    prng = get_prng(prng)
    Pop = list(range(1, n + 1))
    # check if with replacement
    if replace:
        w  = prng.randint(1, n + 1, size = k)
        S = [Pop[i] for i in (w - 1)]
    else: 
        if fast:
            num_sample = min(k, n - k)
        else:
            num_sample = k
        # initialize sample
        S = []
        # sample min of k and n-k indices
        for i in range(num_sample):
            w = prng.randint(1, n - i + 1)
            S.append(Pop[w - 1])
            lastvalue = Pop.pop()
            if w < (n - i):
                Pop[w - 1] = lastvalue # Move last population item to the wth position
        if n - k < k and fast:
            S = list(set(range(1, n + 1)) - set(S))
        
    return np.array(S)


def elimination_sample(k, p, replace=True, prng=None):
    '''
    Weighted random sample of size k from 1, ..., n drawn with or without replacement.
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
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled
    '''
    prng = get_prng(prng)
    weights = np.array(p).astype(float) # ensure the weights are floats
    if any(weights < 0):
        raise ValueError('negative item weight')
    else:
        n = len(weights)
        if replace:
            wc = np.cumsum(weights)/np.sum(weights)  # normalize the weights
            sam = prng.random(size=k)
            return wc.searchsorted(sam)+1
        else:
            if k > n:
                raise ValueError('sample size larger than population in \
                    sample without replacement')
            elif k == n:
                return np.array(range(k))
            else:
                weights_left = np.copy(weights)
                indices_left = list(range(n))
                sam = np.full(k, -1)
                for i in range(k):
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
                return sam+1


def exponential_sample(k, p, prng=None):
    '''
    Weighted random sample of size of size k from 1, ..., n without replacement.

    Let X_1, ..., X_N be independent exponential random variables with rates w_1, ..., w_N,
    and let W = w_1 + ... + w_N.

    Then the chance that X_k is the smallest of them is w_k/W.

    Because of the "memoryless" property of exponential random variables and the independence,
    if the smallest is removed, for j!=k, the chance that X_j is the smallest of the remaining
    variables is w_j/(W-w_k), and so on.

    The percentile function of the exponential distribution with rate w is -ln(1-F)/w.

    Hence, if U~U[0,1], -ln(U)/w ~ exp(w).

    Parameters
    ----------
    k : int
        Desired sample size
    p : 1-D array-like, optional
        The probabilities associated with each value in 1, ... n.
    prng : {None, int, object}
        If prng is None, return a randomly seeded instance of SHA256.
        If prng is an int, return a new SHA256 instance seeded with seed.
        If prng is already a PRNG instance, return it.

    Returns
    -------
    list of items sampled
    '''
    prng = get_prng(prng)
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
        sam = np.array(prng.random(size=n), dtype=float)
        sam = -np.log(sam)/weights
        sample = sam.argsort()[0:k]
        return sample+1

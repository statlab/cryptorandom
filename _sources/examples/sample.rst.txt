Random sampling
---------------

.. code::

    >>> from cryptorandom.cryptorandom import SHA256
    >>> from cryptorandom.sample import random_sample
    >>> import numpy as np

We provide a sampling module compatible with any pseudorandom number generator that has `randint` and `random` methods. The module includes a variety of algorithms for weighted or unweighted sampling, with or without replacement.

The main workhorse is the `random_sample` function. The default sampling algorithm is `sample_by_index`, sampling indices without replacement.

.. code::

    >>> fruit = ['apple', 'banana', 'cherry', 'pear', 'plum']
    >>> s = SHA256(1234567890)
    >>> random_sample(fruit, 2, prng=s)
	array(['plum', 'cherry'], dtype='<U6')


Numpy and the base random module offer methods for drawing simple random samples with and without replacement, but don't allow you to choose the pseudorandom number generator. Numpy's `choice` method uses the Fisher-Yates method to draw a random sample.

.. code::

	>>> np.random.choice(fruit, 2)
	array(['plum', 'apple'], dtype='<U6')

The sampling methods available in `cryptorandom` are below.

================ =========== ======================
Method             weights    replacement
================ =========== ======================
Fisher-Yates      no          without replacement
PIKK              no          without replacement
recursive         no          without replacement
Waterman_R        no          without replacement
Vitter_Z          no          without replacement
sample_by_index   no          without replacement
Exponential       yes         either
Elimination       yes         without replacement
================ =========== ======================

.. code::

    >>> %timeit random_sample(fruit, 2, method="Fisher-Yates", prng=s)
    10000 loops, best of 3: 46.4 µs per loop
    >>> %timeit random_sample(fruit, 2, method="PIKK", prng=s)
    10000 loops, best of 3: 41.3 µs per loop
    >>> %timeit random_sample(fruit, 2, method="recursive", prng=s)
    100000 loops, best of 3: 15 µs per loop
    >>> %timeit random_sample(fruit, 2, method="Waterman_R", prng=s)
    100000 loops, best of 3: 16.9 µs per loop
    >>> %timeit random_sample(fruit, 2, method="Vitter_Z", prng=s)
    10000 loops, best of 3: 22 µs per loop
    >>> %timeit random_sample(fruit, 2, method="sample_by_index", prng=s)
    100000 loops, best of 3: 15 µs per loop
	
	
Some sampling methods (Fisher-Yates, PIKK, sample_by_index, Exponential, and Elimination) return ordered samples, i.e. they are equally likely to return [1, 2] as they are to return [2, 1].

.. code::

    >>> s = SHA256(1234567890)
    >>> counts = {}
    >>> for i in range(10000):
    >>>     sam = pikk(5, 2, prng=s)
    >>>     if str(sam) in counts.keys():
    >>>         counts[str(sam)]+=1
    >>>     else:
    >>>         counts[str(sam)]=0
    >>> counts
	{'[1 2]': 549,
	 '[1 3]': 528,
	 '[1 4]': 512,
	 '[1 5]': 502,
	 '[2 1]': 515,
	 '[2 3]': 485,
	 '[2 4]': 487,
	 '[2 5]': 482,
	 '[3 1]': 484,
	 '[3 2]': 482,
	 '[3 4]': 466,
	 '[3 5]': 525,
	 '[4 1]': 468,
	 '[4 2]': 512,
	 '[4 3]': 490,
	 '[4 5]': 490,
	 '[5 1]': 547,
	 '[5 2]': 460,
	 '[5 3]': 507,
	 '[5 4]': 489}
	 
The reservoir algorithms (Waterman_R and Vitter_Z) and the recursive method aren't guaranteed to randomize the order of sampled items.

.. code::

    >>> s = SHA256(1234567890)
    >>> counts = {}
    >>> for i in range(10000):
    >>>     sam = recursive_sample(5, 2, prng=s)
    >>>     if str(sam) in counts.keys():
    >>>         counts[str(sam)]+=1
    >>>     else:
    >>>         counts[str(sam)]=0
    >>> counts
	{'[1 2]': 492,
	 '[1 3]': 499,
	 '[1 4]': 503,
	 '[1 5]': 1016,
	 '[2 1]': 462,
	 '[2 3]': 487,
	 '[2 4]': 525,
	 '[2 5]': 985,
	 '[3 1]': 481,
	 '[3 2]': 485,
	 '[3 4]': 507,
	 '[3 5]': 984,
	 '[4 1]': 524,
	 '[4 2]': 475,
	 '[4 3]': 516,
	 '[4 5]': 1043}

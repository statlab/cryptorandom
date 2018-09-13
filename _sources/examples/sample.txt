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


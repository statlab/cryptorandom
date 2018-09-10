Random sampling
---------------

.. code::

    >>> from cryptorandom.cryptorandom import SHA256
    >>> from cryptorandom.sample import random_sample
    >>> import numpy as np


Numpy and the base random module offer methods for drawing simple random samples with and without replacement. The default is to use sampling indices without replacement:

.. code::


    >>> fruit = ['apple', 'banana', 'cherry', 'pear', 'plum']
    >>> s = SHA256(1234567890)
    >>> random_sample(fruit, 2, prng=s)
	array(['plum', 'cherry'], dtype='<U6')
	

The sampling methods available are:

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

Below is a time test of the unweighted sampling without replacement methods.


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


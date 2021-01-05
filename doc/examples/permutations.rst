Permuting a list
----------------

.. code::

    >>> from cryptorandom.cryptorandom import SHA256
    >>> from cryptorandom.sample import random_permutation
    >>> import numpy as np


The `sample` module contains methods for generating random permutations, compatible with any pseudorandom number generator that has `randint` and `random` methods. The module includes several algorithms to permute lists or arrays.

The main workhorse is the `random_permutation` function. The default algorithm is `Fisher-Yates`, a shuffling method.

.. code::

    >>> fruit = ['apple', 'banana', 'cherry', 'pear', 'plum']
    >>> s = SHA256(1234567890)
    >>> random_permutation(fruit, prng=s)
	array(['plum', 'apple', 'banana', 'pear', 'cherry'], dtype='<U6')

Numpy and the base random module offer methods for drawing simple random samples with and without replacement, but don't allow you to choose the pseudorandom number generator. Numpy's `choice` method also uses the Fisher-Yates method.

.. code::

	>>> np.random.permutation(fruit) # Returns permuted list
	array(['apple', 'banana', 'plum', 'cherry', 'pear'], dtype='<U6')
	>>> np.random.shuffle(fruit) # Permutes the list in place, returns None
	>>> fruit
	['cherry', 'plum', 'pear', 'banana', 'apple']


The permutation algorithms available are:

================ ===============================================
Method            description
================ ===============================================
Fisher-Yates      a shuffling algorithm
random_sort       generate random floats and sort
permute_by_index  sample integer indices without replacement
================ ===============================================

.. code::

    >>> %timeit random_permutation(fruit, method="Fisher-Yates", prng=s)
    10000 loops, best of 3: 53.3 µs per loop
    >>> %timeit random_permutation(fruit, method="random_sort", prng=s)
    10000 loops, best of 3: 37.5 µs per loop
    >>> %timeit random_permutation(fruit, method="permute_by_index", prng=s)
    10000 loops, best of 3: 22 µs per loop

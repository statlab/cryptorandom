SHA-256 PRNG
------------

.. code::

    from cryptorandom.cryptorandom import SHA256
    import numpy as np

`SHA256` must be instantiated with a seed. We recommend using a large (say, 10-20 digits) integer, but you could use any number or even a string. 

.. code::

    >>> prng = SHA256(1234567890)
    >>> print(prng)
    SHA256 PRNG with seed 1234567890 and counter 0

The PRNG consists of the user-supplied seed and a counter that tracks the number of pseudo-random numbers generated so far. Each time that the PRNG produces a number, one byte gets appended to the input message and the counter is increased by one.

.. code::

    >>> prng.random(5)
    array([0.8654173490455025, 0.9572848101392867, 0.9618334976404997,
       0.24444240654360458, 0.17469471522156924], dtype=object)
    >>> print(prng)
    SHA256 PRNG with seed 1234567890 and counter 5

The `random` method produces floats between 0 and 1. The `randint` method produces random integers on a specified range, using a bit-masking algorithm. Other PRNGs in common software (including the base `random` module and R) use a truncation algorithm to generate random integers, which is known to sample integers non-uniformly.

.. code::

    >>> prng.randint(0, 10, 5)
    array([1, 9, 0, 7, 1])

The `cryptorandom` PRNG inherits methods from the base `random` module. This is useful for permuting lists:

.. code::

   >>> fruit = ['apple', 'banana', 'cherry']
   >>> prng.choice(fruit)
   'cherry'

To generate a single pseudo-random integer, the SHA256 PRNG is only twice the speed of Mersenne Twister.

.. code::

   >>> %timeit prng.randint(0, 200)
   100000 loops, best of 3: 2.1 µs per loop
   >>> %timeit np.random.randint(0, 200)
   1000000 loops, best of 3: 1.11 µs per loop

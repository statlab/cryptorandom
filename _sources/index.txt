Welcome to cryptorandom's documentation!
========================================

`cryptorandom` is a package random sampling and random number generation using
cryptographically secure pseudorandom number generators.

`Download the package on Github`__ or install it from PyPi:

.. code::

	pip install cryptorandom

.. __: https://github.com/statlab/cryptorandom

Questions, comments, and pull requests are welcome.

About
=====

Simple random sampling is drawing k objects from a group of n in such a way that all possible subsets are equally likely. In practice, it is difficult to draw truly random samples. Instead, people tend to draw samples using

1. A **pseudorandom number generator (PRNG)** that produces sequences of bits, plus
2. A **sampling algorithm** that maps pseudorandom numbers into a subset of the population.

A PRNG is a deterministic function that maps its internal state to pseudorandom bits, updates its internal state, and iterates. The internal state of most PRNGs is stored as an integer or matrix with fixed size. As such, the internal state can only take on finitely many values. These PRNGs are periodic: if we generate enough pseudorandom numbers, we will update the internal state so many times that the PRNG will return to its starting state. 

This periodicity is a problem. PRNGs are deterministic, so for each value of the internal state, a sampling algorithm of choice will give us exactly one random sample. If the number of samples of size k from a population of n is greater than the size of the PRNG's state space, then the PRNG cannot possibly generate all samples.

This will certainly be a problem for most PRNGs when n and k grow large, even for those like the Mersenne Twister, which is widely accepted and used as the default PRNG in most common software packages.

Benefits of a Cryptographically Secure PRNG
===========================================
* Infinite state space, no periodicity
* Computationally infeasible to invert, i.e. go from pseudorandom number to internal state
* Outputs are statistically indistinguishable from uniform


API Reference
=============
.. toctree::
   :maxdepth: 2

   api/index.rst
   examples/index.rst

* :ref:`search`


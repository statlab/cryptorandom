cryptorandom
============

|PyPI| |Build Status| |Coverage Status|

Pseudorandom number generator and random sampling using cryptographic
hash functions. The prototype generator is built on SHA-256.

-  **Website:** https://statlab.github.io/cryptorandom
-  **Source:** https://github.com/statlab/cryptorandom
-  **Bug reports:** https://github.com/statlab/cryptorandom/issues

Installation from binaries
--------------------------

::

   $ pip install cryptorandom

Installation from source
------------------------

Install dependencies using:

::

   $ pip install -r requirements.txt

Then, install cryptorandom using:

::

   $ pip install .

If you plan to develop the package, you may run it directly from source:

::

   $ pip install -e .       # Do this once to add pkg to Python path

License information
-------------------

See the file LICENSE for information on the history of this software,
terms & conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.

.. |PyPI| image:: https://img.shields.io/pypi/v/cryptorandom.svg
   :target: https://pypi.org/project/cryptorandom/
.. |Build Status| image:: https://github.com/statlab/cryptorandom/workflows/test/badge.svg?branch=main
   :target: https://github.com/statlab/cryptorandom/actions?query=workflow%3A%22test%22
.. |Coverage Status| image:: https://codecov.io/gh/statlab/cryptorandom/branch/main/graph/badge.svg
   :target: https://app.codecov.io/gh/statlab/cryptorandom/branch/main

[![Build Status](https://travis-ci.org/statlab/cryptorandom.svg?branch=master)](https://travis-ci.org/statlab/cryptorandom)
# cryptorandom
Pseudorandom number generators based on cryptographic hash functions.

The prototype generator is built on SHA256.

- **Source:** [https://github.com/statlab/cryptorandom](https://github.com/statlab/cryptorandom)
- **Bug reports:** [https://github.com/statlab/cryptorandom/issues](https://github.com/statlab/cryptorandom/issues)

## Installation from binaries

```
$ pip install git+git://github.com/statlab/cryptorandom.git
```

## Installation from source

Install dependencies using:

```
$ pip install -r requirements.txt
```

Then, install permute using:

```
$ pip install .
```

If you plan to develop the package, you may run it directly from source:

```
$ pip install -e .       # Do this once to add pkg to Python path
```

## License information

See the file LICENSE for information on the history of this software, terms
& conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.
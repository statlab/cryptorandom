#! /usr/bin/env python

descr = """Pseudorandom number generator and random sampling using cryptographic hash functions

"""

import os


DISTNAME = 'cryptorandom'
DESCRIPTION = 'Pseudorandom number generator and random sampling using cryptographic hash functions'
LONG_DESCRIPTION = descr
AUTHOR = 'Kellie Ottoboni and Philip B. Stark'
AUTHOR_EMAIL = 'kellieotto@berkeley.edu'
URL = 'http://www.github.com/statlab/cryptorandom'
LICENSE = 'BSD License'
DOWNLOAD_URL = 'http://www.github.com/statlab/cryptorandom'
VERSION = '0.2'
PYTHON_VERSION = (2, 7)

INSTALL_REQUIRES = [
    'numpy',
    'scipy'
]

TESTS_REQUIRE = [
    'coverage',
    'nose',
    'flake8'
]


def write_version_py(filename='cryptorandom/version.py'):
    template = """# THIS FILE IS GENERATED FROM THE CRYPTORANDOM SETUP.PY
version='%s'
"""

    try:
        fname = os.path.join(os.path.dirname(__file__), filename)
        with open(fname, 'w') as f:
            f.write(template % VERSION)
    except IOError:
        raise IOError("Could not open/write to cryptorandom/version.py - did you "
                      "install using sudo in the past? If so, run\n"
                      "sudo chown -R your_username ./*\n"
                      "from package root to fix permissions, and try again.")


if __name__ == "__main__":

    write_version_py()

    from setuptools import setup
    setup(
        name=DISTNAME,
        version=VERSION,
        license=LICENSE,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        download_url=DOWNLOAD_URL,

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Scientific/Engineering',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
        ],

        install_requires=INSTALL_REQUIRES,
        tests_require=TESTS_REQUIRE,

        packages=['cryptorandom', 'cryptorandom.tests',],
    )

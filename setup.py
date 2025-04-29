import sys
from setuptools import setup



if sys.version_info[:2] < (3, 11):
    error = (
        "cryptorandom 0.4+ requires Python 3.11 or later (%d.%d detected). \n"
        % sys.version_info[:2]
    )
    sys.stderr.write(error + "\n")
    sys.exit(1)

DISTNAME = 'cryptorandom'
DESCRIPTION = 'Pseudorandom number generator and random sampling using cryptographic hash functions'
AUTHOR = 'Amanda Glazer, Kellie Ottoboni, Philip B. Stark'
AUTHOR_EMAIL = 'pbstark@berkeley.edu'
URL = 'http://www.github.com/statlab/cryptorandom'
LICENSE = 'BSD License'
DOWNLOAD_URL = 'http://www.github.com/statlab/cryptorandom'

with open("cryptorandom/__init__.py") as fid:
    for line in fid:
        if line.startswith("__version__"):
            VERSION = line.strip().split()[-1][1:-1]
            break

with open("README.rst") as fh:
    LONG_DESCRIPTION = fh.read()

def parse_requirements_file(filename):
    with open(filename, encoding="utf-8") as fid:
        requires = [l.strip() for l in fid.readlines() if l]

    return requires


INSTALL_REQUIRES = parse_requirements_file("requirements/default.txt")
TESTS_REQUIRE = parse_requirements_file("requirements/test.txt")


if __name__ == "__main__":

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
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13',
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

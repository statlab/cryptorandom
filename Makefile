.PHONY: all clean test

all:
	python setup.py build_ext --inplace

clean:
	find . -name "*.so" -o -name "*.pyc" -o -name "*.pyx.md5" | xargs rm -f
	rm -rf build dist cryptorandom.egg-info
	rm -rf .ipynb_checkpoints .coverage .cache

test:
	nosetests cryptorandom -A 'not slow' --ignore-files=^_test -v -s

test-all:
	nosetests cryptorandom --ignore-files=^_test -v -s

doctest:
	nosetests cryptorandom --ignore-files=^_test -v -s --with-doctest --ignore-files=^\. --ignore-files=^setup\.py$$ --ignore-files=test

coverage:
	nosetests cryptorandom --with-coverage --cover-package=cryptorandom --ignore-files=^_test  -v -s
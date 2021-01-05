.PHONY: all clean test

all:
	python setup.py build_ext --inplace

clean:
	find . -name "*.so" -o -name "*.pyc" -o -name "*.pyx.md5" | xargs rm -f
	rm -rf build dist cryptorandom.egg-info
	rm -rf .ipynb_checkpoints .coverage .cache

test:
	#pytest --durations=10 --pyargs cryptorandom
	pytest --durations=10

test-all: test
	# TODO

doctest:
	pytest --doctest-modules --durations=10 --pyargs cryptorandom

coverage:
	# pytest --cov=cryptorandom --doctest-modules --durations=10 --pyargs cryptorandom
	pytest --cov=cryptorandom --durations=10

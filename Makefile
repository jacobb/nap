VERSION=0.0.1
default: test

test:
	py.test

coverage:
	py.test --cov nap --cov-report html

.PHONY: build watch

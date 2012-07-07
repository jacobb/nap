VERSION=0.0.1
default: test

test:
	py.test

coverage:
	py.test --cov login_service --cov-report html

.PHONY: build watch

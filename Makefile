SHELL = /bin/bash
BLACK=black

all: lint

lint:
	$(BLACK) --check .

black:
	$(BLACK) .


.PHONY: test/prepare
test/prepare:
	@python setup.py develop

.PHONY: test/clean
test/clean:
	@rm -rf fasjson.egg-info

.PHONY: test/code
test/code:
	@mypy ./fasjson

.PHONY: test/unit
test/unit:
	@py.test -s

.PHONY: test
test: test/code test/unit test/clean
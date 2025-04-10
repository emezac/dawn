.PHONY: install install-dev lint format test

install:
	pip install -e .

install-dev:
	pip install -e . && pip install -r requirements-dev.txt

lint:
	flake8 .

format:
	isort .
	black .

test:
	pytest

setup-hooks:
	pre-commit install

lint-all: format lint

ci: lint-all test 
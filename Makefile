PROJECT_NAME := $(shell python setup.py --name)
PROJECT_VERSION := $(shell python setup.py --version)
SOURCE_ROOT := "src/$(PROJECT_NAME)"

BOLD := \033[1m
RESET := \033[0m

default: help

.PHONY : help
help:  ## Show this help
	@echo "$(BOLD)$(PROJECT_NAME) project Makefile $(RESET)"
	@echo "Please use 'make $(BOLD)target$(RESET)' where $(BOLD)target$(RESET) is one of:"
	@grep -h ':\s\+##' Makefile | column -t -s# | awk -F ":" '{ print "  $(BOLD)" $$1 "$(RESET)" $$2 }'

.PHONY: install
install:  ## Install the project in the current environment, with its dependencies
	@echo "$(BOLD)Installing $(PROJECT_NAME) $(PROJECT_VERSION)$(RESET)"
	@pip install uv
	@uv pip install .

.PHONY: dev
dev:  ## Install the project in the current environment, with its dependencies, including the ones needed in a development environment
	@echo "$(BOLD)Installing (or upgrading) $(PROJECT_NAME) $(PROJECT_VERSION) in dev mode (with all dependencies)$(RESET)"
	@pip install --upgrade pip setuptools uv
	@uv pip install --upgrade -e .[dev,lint,tests]
	@$(MAKE) full-clean

.PHONY: build
build:  ## Build the package
build: clean
	@echo "$(BOLD)Building package$(RESET)"
	@python -m build -w --installer uv

.PHONY: clean
clean:  ## Clean python build related directories and files
	@echo "$(BOLD)Cleaning$(RESET)"
	@rm -rf build dist $(SOURCE_ROOT).egg-info

.PHONY: full-clean
full-clean:  ## Like "clean" but will clean some other generated directories or files
full-clean: clean
	@echo "$(BOLD)Full cleaning$(RESET)"
	find ./ -type d  \( -name '__pycache__' -or -name '.pytest_cache' -or -name '.mypy_cache'  \) -print0 | xargs -tr0 rm -r

.PHONY: tests test
test / tests:  ## Run tests for the whole project.
test: tests  # we allow "test" and "tests"
tests:
	@echo "$(BOLD)Running tests$(RESET)"
	@## we ignore error 5 from pytest meaning there is no test to run
	@pytest || ( ERR=$$?; if [ $${ERR} -eq 5 ]; then (exit 0); else (exit $${ERR}); fi )

.PHONY: tests-nocapture test-nocapture
test-nocapture / tests-nocapture:  ## Run tests for the whole project without capturing stdout
test-nocapture: tests-nocapture  # we allow "test-nocapture" and "tests-nocapture"
tests-nocapture:
	@echo "$(BOLD)Running tests without capturing (pytest -s)$(RESET)"
	@## we ignore error 5 from pytest meaning there is no test to run
	@pytest -s || ( ERR=$$?; if [ $${ERR} -eq 5 ]; then (exit 0); else (exit $${ERR}); fi )

.PHONY: tests-fail-fast
test-fail-fast / test-fast / tests-fast / test-fail / tests-fail / tests-fail-fast:  ## Run tests for the whole project without coverage, stopping at the first failure.
test-fail-fast: tests-fail-fast
test-fast: tests-fail-fast
tests-fast: tests-fail-fast
test-fail: tests-fail-fast
tests-fail: tests-fail-fast
tests-fail-fast:
	@echo "$(BOLD)Running tests (without coverage, stopping at first failure)$(RESET)"
	@## we ignore error 5 from pytest meaning there is no test to run
	@pytest -x --no-cov || ( ERR=$$?; if [ $${ERR} -eq 5 ]; then (exit 0); else (exit $${ERR}); fi )

.PHONY: lint
lint:  ## Run all linters (check-isort, check-black, mypy, ruff)
lint: check-isort check-black ruff mypy

.PHONY: check checks
check / checks:  ## Run all checkers (lint, tests)
check: checks
checks: lint tests

.PHONY: mypy
mypy:  ## Run the mypy tool
	@echo "$(BOLD)Running mypy$(RESET)"
	@mypy $(SOURCE_ROOT)

.PHONY: check-isort
check-isort:  ## Run the isort tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking isort(RESET)"
	@isort $(SOURCE_ROOT) --check-only 2>&1

.PHONY: check-black
check-black:  ## Run the black tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking black$(RESET)"
	@black --target-version py310 --check  $(SOURCE_ROOT) 2>&1

.PHONY: ruff
ruff:  ## Run the ruff tool
	@echo "$(BOLD)Running ruff$(RESET)"
	@ruff check $(SOURCE_ROOT) --extend-select RUF100

.PHONY: ruff-fix
ruff-fix:  ## Run the ruff tool in fix mode
	@echo "$(BOLD)Running ruff$(RESET) in fix only mode"
	@ruff check --fix --exit-zero $(SOURCE_ROOT) --extend-select RUF100

.PHONY: pretty format
pretty / format:  ## Run all code beautifiers (ruff-fix, isort, black)
pretty: format
format: ruff-fix isort black

.PHONY: isort
isort:  ## Run the isort tool and update files that need to
	@echo "$(BOLD)Running isort$(RESET)"
	@isort $(SOURCE_ROOT) --atomic

.PHONY: black
black:  ## Run the black tool and update files that need to
	@echo "$(BOLD)Running black$(RESET)"
	@black --target-version py310 $(SOURCE_ROOT)

.PHONY: archive
archive:  ## Create a text archive suitable for AI chatbots
	@echo "$(BOLD)Creating archive$(RESET)"
	$(shell ( echo pyproject.toml; echo README.md; find src/ -name '*.py' ) | while read a; do echo "\n\n## File: $$a\n"; cat $$a; done > $(PROJECT_NAME)-sources.txt )

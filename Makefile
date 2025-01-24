.PHONY: setup clean test lint install run help format dev-setup

# Python and virtualenv settings
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

create-venv:  ## Create virtual environment
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip setuptools wheel

install-dev: create-venv  ## Install development dependencies
	$(BIN)/pip install -e ".[dev]"

install-test: create-venv  ## Install test dependencies
	$(BIN)/pip install -e ".[test]"

install: create-venv  ## Install all dependencies
	$(BIN)/pip install -e ".[dev,test]"
	$(BIN)/playwright install firefox

clean:  ## Clean up generated files and virtual environment
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf build/
	rm -rf dist/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf docs/html/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".eggs" -exec rm -rf {} +

setup: clean install  ## Full setup: clean and install everything

test: install-test  ## Run tests
	$(BIN)/pytest

lint: install-dev  ## Run all linting checks
	$(BIN)/yapf -ir src/ tests/

format: lint  ## Format code (alias for lint)

run: install  ## Run the crawler with default settings
	$(BIN)/python src/main.py

build: clean install test lint  ## Build the project: clean, install, test, and lint

dev-clean: clean  ## Clean development files
	rm -rf results.json
	rm -rf nohup*.out

dev-setup: setup  ## Setup development environment
	git config core.hooksPath .githooks/

check: install-test install-dev  ## Run all checks (tests and linting)
	$(BIN)/pytest
	$(BIN)/yapf -dr src/ tests/
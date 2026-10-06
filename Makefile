.DEFAULT_GOAL := help

.PHONY: help install run test lint fmt cov

help: ## Show available commands
	@awk -F ':.*## ' '/^[a-z-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install application and development dependencies
	uv sync --locked

run: ## Start the development server on port 8000
	uv run --locked python wsgi.py

test: ## Run the test suite
	uv run --locked pytest

lint: ## Check Python lint and formatting with Ruff
	uv run --locked ruff check .
	uv run --locked ruff format --check .

fmt: ## Format Python code with Ruff
	uv run --locked ruff format .

cov: ## Run tests with coverage and show missing lines
	uv run --locked pytest --cov=app --cov-report=term-missing

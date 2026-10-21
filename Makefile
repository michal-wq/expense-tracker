.DEFAULT_GOAL := help

IMAGE ?= expense-tracker
TAG ?= local
PORT ?= 8000

.PHONY: help install run test lint fmt cov build verify-package docker-build docker-run docker-test

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

build: ## Build wheel and source distributions in dist/
	uv build

verify-package: build ## Run tests against the installed wheel in a separate environment
	@package_check="$$(mktemp -d)"; \
	uv venv "$$package_check/.venv" --python .venv/bin/python && \
	uv pip install --python "$$package_check/.venv/bin/python" dist/*.whl pytest && \
	cp -R tests "$$package_check/tests" && \
	"$$package_check/.venv/bin/python" -I -m pytest -q -c /dev/null \
		--rootdir "$$package_check" "$$package_check/tests"

docker-build: ## Build the Docker image (IMAGE and TAG are configurable)
	docker build -t "$(IMAGE):$(TAG)" .

docker-run: ## Run the Docker image on localhost (default PORT=8000)
	docker run --rm -p "127.0.0.1:$(PORT):8000" "$(IMAGE):$(TAG)"

docker-test: docker-build ## Build the Docker image and check its HTTP endpoints
	DOCKER_IMAGE="$(IMAGE):$(TAG)" uv run --locked pytest checks/test_docker.py

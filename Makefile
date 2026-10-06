.DEFAULT_GOAL := help

.PHONY: help install

help: ## Show available commands
	@awk -F ':.*## ' '/^[a-z-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install application and development dependencies
	uv sync --locked

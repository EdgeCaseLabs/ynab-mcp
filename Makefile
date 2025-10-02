.PHONY: help install dev test lint format inspect clean build

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	uv sync

dev: ## Install development dependencies
	uv sync --all-extras

test: ## Run tests
	uv run pytest

lint: ## Run linting
	uv run ruff ynab_mcp_server/

format: ## Format code
	uv run black ynab_mcp_server/

typecheck: ## Run type checking
	uv run mypy ynab_mcp_server/

inspect: ## Run MCP inspector with debug logging
	npx @modelcontextprotocol/inspector uv run --directory $(PWD) python -m ynab_mcp_server --logging

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

build: ## Build package
	uv build

run: ## Run server with debug logging
	uv run python -m ynab_mcp_server --logging

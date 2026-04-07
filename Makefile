.DEFAULT_GOAL := help

.PHONY: help format lint typecheck test quality-gate deps-direct deps-tree deps-outdated deps-audit deps-report

help: ## List available targets.
	@awk 'BEGIN {FS = ":.*## "; printf "Available targets:\n"} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-14s %s\n", $$1, $$2}' Makefile

# Quality checks
format: ## Run auto-fixes and formatting.
	uv run ruff check . --fix
	uv run ruff format .

lint: ## Run lint checks.
	uv run ruff check .

typecheck: ## Run static type checks.
	uv run mypy .

test: ## Run the test suite.
	uv run pytest

quality-gate: format lint typecheck test ## Run the full local quality gate.

# Dependency inspection
deps-direct: ## List direct dependencies.
	@uv run python scripts/list_direct_dependencies.py

deps-tree: ## Show the full dependency tree.
	uv tree --frozen

deps-outdated: ## Show outdated top-level dependencies.
	uv tree --frozen --depth 1 --outdated

deps-audit: ## Audit dependencies for known vulnerabilities.
	mkdir -p .tmp
	uv export --frozen --no-hashes --format requirements-txt -o .tmp/requirements-audit.txt
	uvx --from pip-audit pip-audit -r .tmp/requirements-audit.txt

deps-report: deps-direct deps-outdated deps-audit ## Run the dependency reporting targets.

.PHONY: install test lint typecheck validate check build clean

install:            ## Create venv and install dev dependencies
	uv sync --extra dev

test:               ## Run the test suite
	uv run pytest

lint:               ## Lint and check formatting
	uv run ruff check src tests skills/article-craft/scripts
	uv run ruff format --check src tests skills/article-craft/scripts

format:             ## Auto-format
	uv run ruff format src tests skills/article-craft/scripts
	uv run ruff check --fix src tests skills/article-craft/scripts

typecheck:          ## Static type checking
	uv run mypy src

validate:           ## Validate the Agent Skill structure
	uv run python skills/article-craft/scripts/validate_skill.py

check: lint typecheck test validate  ## Everything CI runs

build:              ## Build sdist and wheel
	uv build

clean:              ## Remove caches and build artifacts
	rm -rf dist build .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov

.PHONY: checks fixes tests

checks:
	uv run ruff format --check
	uv run ruff check
	uv run pyright

fixes:
	uv run ruff format
	uv run ruff check --fix

tests:
	uv run pytest

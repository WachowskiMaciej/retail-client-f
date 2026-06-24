VENV := .venv
PY := $(VENV)/bin/python
BIN := $(VENV)/bin


setup:
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"

# Default test target: unit tests only, no network.
test:
	$(BIN)/pytest tests/unit

# Integration tests hit the real API. Needs GOREST_TOKEN in the environment.
test-integration:
	$(BIN)/pytest -m integration tests/integration

# Check only: lint rules + that files are formatted. Fails on any deviation.
lint:
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

# Auto-fix: apply safe lint fixes, then reformat in place.
format:
	$(BIN)/ruff check --fix .
	$(BIN)/ruff format .

typecheck:
	$(BIN)/mypy

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

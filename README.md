# retail-client

Typed Python client for store-worker task management, wrapping the [GoREST](https://gorest.co.in/) public REST API.

## Prerequisites

- Python 3.12+
- A GoREST token — register free at https://gorest.co.in/consumer/login (takes ~30 seconds)

## Setup

```bash
make setup
```

This creates a `.venv` and installs the package with all dev dependencies.

## Configuration

Copy `.env.example` to `.env` and fill in your token:

```bash
cp .env.example .env
# edit .env and set GOREST_TOKEN=your-token-here
```

The `.env` file is loaded automatically before tests run.

## Running tests

Unit tests (no network, no token required):

```bash
make test
```

Integration tests (hit the real GoREST API, token required):

```bash
make test-integration
```

## Other commands

```bash
make lint        # check linting and formatting
make format      # auto-fix linting and formatting
make typecheck   # mypy strict mode
make clean       # remove cache directories
```

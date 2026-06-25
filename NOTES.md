# Notes

## Key design decisions

**Separate `HttpExecutor` layer.** Retry logic, auth headers, and error mapping live in `HttpExecutor`, not in `RetailClient`. This keeps the public client clean and makes retry/timeout behavior testable in isolation without mocking the full client.

**`RetryPolicy` as a frozen dataclass.** Retry configuration is explicit and immutable — callers can swap it out via `ClientConfig`, and tests can pass `RetryPolicy(max_attempts=1)` to disable retries. The alternative (hardcoding retry behavior) would make tests flaky and behavior opaque.

**Pydantic v2 for models.** Gives free validation, serialization, and typed access. Tradeoff: adds a dependency and couples the public API to Pydantic — but for a typed client library this is the right call.

**`respx` for unit test HTTP mocking.** Intercepts at the transport layer, so tests exercise real `httpx` request/response flow. The alternative (`unittest.mock`) would mock too high and miss serialization bugs.

**Faker with `.unique` for integration test data.** Prevents email collisions on GoREST's uniqueness constraint across parallel or repeated runs. Each fixture factory registers teardown — resources are deleted even if the test fails mid-way.

## What I would add with another 4 hours

- More integration tests covering validation error messages
- Structured logging of requests and retries via the `logging` module
- Parallel integration test runs with `pytest-xdist`
- GitHub Actions CI running unit tests on every push

## Where LLM assistance helped and where it misled

**Helped:** 
 - Boilerplate for Pydantic models, 
 - errors structure, 
 - respx mock patterns, 
 - help make_executor factory.

**Misled:** 
 - The initial client used `GET /users/{id}/todos` for listing tasks — this endpoint does not exist on GoREST. The correct endpoint is `GET /todos?user_id={id}`. 
 - It assumed `GET /users/{id}` was unauthenticated, which caused 404s in integration tests — GoREST requires a token for individual user lookups. 
 - Some of created code was unnecessary and could be simplified
 - A lot of unuseful comments
 - Misleading typing in few places

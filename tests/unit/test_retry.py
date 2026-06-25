import httpx
import pytest

from retail_client.config import RetryPolicy
from retail_client.errors import APIError, RequestTimeoutError, ServerError

from .conftest import ExecutorFactory


def test_retries_transient_5xx_then_succeeds(make_executor: ExecutorFactory) -> None:
    setup = make_executor([httpx.Response(503), httpx.Response(200, json={"ok": True})])

    response = setup.executor.request("GET", "/users")

    assert response.status_code == 200
    assert len(setup.delays) == 1  # slept once, between the two attempts


def test_gives_up_after_max_attempts_and_raises_last_status(
    make_executor: ExecutorFactory,
) -> None:
    setup = make_executor(
        [httpx.Response(503), httpx.Response(503), httpx.Response(503)],
        retry=RetryPolicy(max_attempts=3),
    )

    with pytest.raises(ServerError) as excinfo:
        setup.executor.request("GET", "/users")

    assert excinfo.value.status_code == 503
    assert len(setup.delays) == 2  # three attempts -> two waits


def test_does_not_retry_client_errors(make_executor: ExecutorFactory) -> None:
    # A 400 is the caller's fault; retrying would just waste time.
    setup = make_executor([httpx.Response(400)])

    with pytest.raises(APIError) as excinfo:
        setup.executor.request("GET", "/users")

    assert excinfo.value.status_code == 400
    assert setup.delays == []


def test_backs_off_exponentially_between_retries(make_executor: ExecutorFactory) -> None:
    setup = make_executor(
        [httpx.Response(503), httpx.Response(503), httpx.Response(200, json={})],
        retry=RetryPolicy(max_attempts=3, base_delay_seconds=0.5, multiplier=2.0),
    )

    setup.executor.request("GET", "/users")

    assert setup.delays == [0.5, 1.0]


def test_retries_on_timeout_then_raises_timeout_error(make_executor: ExecutorFactory) -> None:
    setup = make_executor(
        [httpx.ConnectTimeout("slow"), httpx.ConnectTimeout("slow")],
        retry=RetryPolicy(max_attempts=2),
    )

    with pytest.raises(RequestTimeoutError):
        setup.executor.request("GET", "/users")

    assert len(setup.delays) == 1


def test_retry_after_mechanism(make_executor: ExecutorFactory) -> None:
    setup = make_executor(
        [
            httpx.Response(429, headers={"Retry-After": "2"}),
            httpx.Response(429, headers={"Retry-After": "2"}),
            httpx.Response(200, json={}),
        ],
        retry=RetryPolicy(max_attempts=3, base_delay_seconds=0.5, multiplier=2.0),
    )

    setup.executor.request("GET", "/users")

    assert setup.delays == [2.0, 2.0]

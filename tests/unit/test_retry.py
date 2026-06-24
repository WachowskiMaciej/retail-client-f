import httpx
import pytest

from retail_client.config import RetryPolicy
from retail_client.errors import APIError, RequestTimeoutError, ServerError

from .conftest import ExecutorFactory


def test_retries_transient_5xx_then_succeeds(make_executor: ExecutorFactory) -> None:
    executor, delays = make_executor([httpx.Response(503), httpx.Response(200, json={"ok": True})])

    response = executor.request("GET", "/users")

    assert response.status_code == 200
    assert len(delays) == 1  # slept once, between the two attempts


def test_gives_up_after_max_attempts_and_raises_last_status(
    make_executor: ExecutorFactory,
) -> None:
    executor, delays = make_executor(
        [httpx.Response(503), httpx.Response(503), httpx.Response(503)],
        retry=RetryPolicy(max_attempts=3),
    )

    with pytest.raises(ServerError) as excinfo:
        executor.request("GET", "/users")

    assert excinfo.value.status_code == 503
    assert len(delays) == 2  # three attempts -> two waits


def test_does_not_retry_client_errors(make_executor: ExecutorFactory) -> None:
    # A 400 is the caller's fault; retrying would just waste time.
    executor, delays = make_executor([httpx.Response(400)])

    with pytest.raises(APIError) as excinfo:
        executor.request("GET", "/users")

    assert excinfo.value.status_code == 400
    assert delays == []


def test_waits_a_fixed_delay_between_retries(make_executor: ExecutorFactory) -> None:
    executor, delays = make_executor(
        [httpx.Response(503), httpx.Response(503), httpx.Response(200, json={})],
        retry=RetryPolicy(max_attempts=3, delay_seconds=0.5),
    )

    executor.request("GET", "/users")

    assert delays == [0.5, 0.5]  # same wait each time


def test_retries_on_timeout_then_raises_timeout_error(make_executor: ExecutorFactory) -> None:
    executor, delays = make_executor(
        [httpx.ConnectTimeout("slow"), httpx.ConnectTimeout("slow")],
        retry=RetryPolicy(max_attempts=2),
    )

    with pytest.raises(RequestTimeoutError):
        executor.request("GET", "/users")

    assert len(delays) == 1

import httpx
import pytest

from retail_client.config import RetryPolicy
from retail_client.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

from .conftest import ExecutorFactory


@pytest.mark.parametrize(
    "status, error_type",
    [
        (401, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitError),
    ],
)
def test_status_maps_to_error(
    make_executor: ExecutorFactory, status: int, error_type: type
) -> None:
    setup = make_executor([httpx.Response(status)], retry=RetryPolicy(max_attempts=1))

    with pytest.raises(error_type) as excinfo:
        setup.executor.request("GET", "/users")

    assert excinfo.value.status_code == status


def test_422_carries_field_level_details(make_executor: ExecutorFactory) -> None:
    body = [{"field": "email", "message": "has already been taken"}]
    setup = make_executor([httpx.Response(422, json=body)])

    with pytest.raises(ValidationError) as excinfo:
        setup.executor.request("POST", "/users", authenticated=True)

    assert excinfo.value.details == body
    assert "email" in str(excinfo.value)

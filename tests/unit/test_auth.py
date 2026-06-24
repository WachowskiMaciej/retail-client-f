import httpx
import pytest
import respx

from retail_client import ClientConfig, Gender, RetailClient, UserCreate
from retail_client.errors import AuthenticationError

BASE = "https://gorest.co.in/public/v2"


def test_authenticated_call_without_token_fails_before_any_request() -> None:
    with RetailClient(ClientConfig(token=None)) as client, pytest.raises(AuthenticationError):
        client.create_user(UserCreate(name="Dana", email="d@example.com", gender=Gender.female))


@respx.mock
def test_read_operations_send_no_authorization_header() -> None:
    """
    Validate that read operations are not sending token even if it is configured.
    """
    route = respx.get(f"{BASE}/users").mock(return_value=httpx.Response(200, json=[]))

    with RetailClient(ClientConfig(token="secret")) as client:
        client.list_users()

    assert "Authorization" not in route.calls.last.request.headers


@respx.mock
def test_write_operations_send_bearer_token() -> None:
    """
    Validate that write operations are sending bearer token.
    """
    route = respx.post(f"{BASE}/users").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 1,
                "name": "Dana",
                "email": "d@example.com",
                "gender": "female",
                "status": "active",
            },
        )
    )
    with RetailClient(ClientConfig(token="secret")) as client:
        client.create_user(UserCreate(name="Dana", email="d@example.com", gender=Gender.female))

    assert route.calls.last.request.headers["Authorization"] == "Bearer secret"

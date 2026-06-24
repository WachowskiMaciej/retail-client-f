import pytest
from faker import Faker

from retail_client import ClientConfig, Gender, RetailClient, User
from retail_client.errors import NotFoundError, ValidationError

pytestmark = pytest.mark.integration

_fake = Faker()


def test_list_users_works_without_a_token() -> None:
    # The unauthenticated path: a token-less client can still read.
    with RetailClient(ClientConfig(token=None)) as anonymous:
        users = anonymous.list_users(per_page=5)

    assert isinstance(users, list)
    assert all(isinstance(u, User) for u in users)


def test_create_then_fetch_user_round_trips(client: RetailClient, workers) -> None:
    created = workers(name=_fake.name())

    fetched = client.get_user(created.id)

    assert fetched.id == created.id
    assert fetched.name == created.name
    assert fetched.gender is Gender.female


def test_deleting_a_user_makes_it_unreachable(client: RetailClient, workers) -> None:
    user = workers()

    client.delete_user(user.id)

    with pytest.raises(NotFoundError):
        client.get_user(user.id)


def test_create_user_with_invalid_email_raises_validation(client: RetailClient) -> None:
    from retail_client import UserCreate

    # Malformed payload is rejected server-side, so nothing is created and
    # there is nothing to clean up.
    with pytest.raises(ValidationError) as excinfo:
        client.create_user(UserCreate(name="Bad Email", email="not-an-email", gender=Gender.male))

    assert excinfo.value.status_code == 422

import contextlib
import os
from collections.abc import Iterator

import pytest
from faker import Faker

from retail_client import (
    ClientConfig,
    Gender,
    RetailClient,
    Task,
    TaskCreate,
    User,
    UserCreate,
)
from retail_client.errors import NotFoundError

_fake = Faker()


def _unique_email() -> str:
    return _fake.unique.email()


@pytest.fixture(scope="session")
def token() -> str:
    value = os.environ.get("GOREST_TOKEN")
    if not value:
        pytest.skip("GOREST_TOKEN is not set; skipping integration tests")
    return value


@pytest.fixture
def client(token: str) -> Iterator[RetailClient]:
    with RetailClient(ClientConfig(token=token)) as instance:
        yield instance


@pytest.fixture
def workers(client: RetailClient):
    created: list[int] = []

    def make(name: str = "Store Worker", gender: Gender = Gender.female) -> User:
        user = client.create_user(UserCreate(name=name, email=_unique_email(), gender=gender))
        created.append(user.id)
        return user

    yield make

    for user_id in created:
        with contextlib.suppress(NotFoundError):
            client.delete_user(user_id)


@pytest.fixture
def tasks(client: RetailClient):
    created: list[int] = []

    def make(user_id: int, title: str = "Restock shelves") -> Task:
        task = client.create_task(user_id, TaskCreate(title=title))
        created.append(task.id)
        return task

    yield make

    for task_id in created:
        with contextlib.suppress(NotFoundError):
            client.delete_task(task_id)

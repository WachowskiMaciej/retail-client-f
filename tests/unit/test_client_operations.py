import json
from datetime import datetime

import httpx
import respx

from retail_client import (
    ClientConfig,
    RetailClient,
    Task,
    TaskCreate,
    TaskStatus,
    User,
    UserStatus,
)

BASE = "https://gorest.co.in/public/v2"


@respx.mock
def test_list_users_returns_typed_models() -> None:
    payload = [
        {"id": 1, "name": "Ada", "email": "ada@x.com", "gender": "female", "status": "active"},
        {"id": 2, "name": "Linus", "email": "linus@x.com", "gender": "male", "status": "inactive"},
    ]
    respx.get(f"{BASE}/users").mock(return_value=httpx.Response(200, json=payload))

    with RetailClient() as client:
        users = client.list_users()

    assert all(isinstance(u, User) for u in users)
    assert users[0].name == "Ada"
    assert users[1].status is UserStatus.inactive


@respx.mock
def test_list_users_forwards_pagination_params() -> None:
    route = respx.get(f"{BASE}/users").mock(return_value=httpx.Response(200, json=[]))

    with RetailClient() as client:
        client.list_users(page=3, per_page=50)

    assert route.calls.last.request.url.params["page"] == "3"
    assert route.calls.last.request.url.params["per_page"] == "50"


@respx.mock
def test_list_user_tasks_returns_typed_models() -> None:
    payload = [
        {"id": 1, "user_id": 5, "title": "Restock", "due_on": None, "status": "pending"},
        {"id": 2, "user_id": 5, "title": "Sweep", "due_on": None, "status": "completed"},
    ]
    route = respx.get(f"{BASE}/todos").mock(return_value=httpx.Response(200, json=payload))

    with RetailClient(ClientConfig(token="t")) as client:
        tasks = client.list_user_tasks(5)

    assert route.calls.last.request.url.params["user_id"] == "5"
    assert all(isinstance(t, Task) for t in tasks)
    assert tasks[0].title == "Restock"


@respx.mock
def test_create_task_serializes_enum_and_datetime() -> None:
    due = datetime(2026, 7, 1, 9, 30)
    route = respx.post(f"{BASE}/users/1/todos").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 10,
                "user_id": 1,
                "title": "Restock aisle 4",
                "due_on": "2026-07-01T09:30:00",
                "status": "pending",
            },
        )
    )

    with RetailClient(ClientConfig(token="t")) as client:
        task = client.create_task(
            1, TaskCreate(title="Restock aisle 4", due_on=due, status=TaskStatus.pending)
        )
    sent = json.loads(route.calls.last.request.content)
    assert sent["status"] == "pending"
    assert sent["due_on"].startswith("2026-07-01T09:30:00")
    assert isinstance(task, Task)
    assert task.id == 10


@respx.mock
def test_create_task_omits_optional_due_on_when_not_set() -> None:
    route = respx.post(f"{BASE}/users/1/todos").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 11,
                "user_id": 1,
                "title": "Count till",
                "due_on": None,
                "status": "pending",
            },
        )
    )

    with RetailClient(ClientConfig(token="t")) as client:
        client.create_task(1, TaskCreate(title="Count till"))

    sent = json.loads(route.calls.last.request.content)
    assert "due_on" not in sent


@respx.mock
def test_complete_task_patches_status_to_completed() -> None:
    route = respx.patch(f"{BASE}/todos/12").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 12,
                "user_id": 1,
                "title": "Sweep",
                "due_on": None,
                "status": "completed",
            },
        )
    )

    with RetailClient(ClientConfig(token="t")) as client:
        task = client.complete_task(12)

    sent = json.loads(route.calls.last.request.content)
    assert sent == {"status": "completed"}
    assert task.status is TaskStatus.completed


@respx.mock
def test_delete_task_returns_none_on_204() -> None:
    respx.delete(f"{BASE}/todos/12").mock(return_value=httpx.Response(204))

    with RetailClient(ClientConfig(token="t")) as client:
        assert client.delete_task(12) is None

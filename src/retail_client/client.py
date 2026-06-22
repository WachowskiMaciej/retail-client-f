"""Public client."""

from typing import Any

import httpx

from .config import ClientConfig
from .http import HttpExecutor
from .models import Task, TaskCreate, TaskStatus, User, UserCreate


class RetailClient:
    def __init__(
        self,
        config: ClientConfig | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._config = config or ClientConfig()
        self._client = httpx.Client(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            transport=transport,
        )
        self._http = HttpExecutor(self._client, self._config.retry, token=self._config.token)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "RetailClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def list_users(self, *, page: int = 1, per_page: int = 20) -> list[User]:
        """Unauthenticated read."""
        response = self._http.request("GET", "/users", params={"page": page, "per_page": per_page})
        return [User.model_validate(item) for item in response.json()]

    def get_user(self, user_id: int) -> User:
        """Unauthenticated read."""
        response = self._http.request("GET", f"/users/{user_id}")
        return User.model_validate(response.json())

    def create_user(self, data: UserCreate) -> User:
        response = self._http.request("POST", "/users", json=_dump(data), authenticated=True)
        return User.model_validate(response.json())

    def delete_user(self, user_id: int) -> None:
        self._http.request("DELETE", f"/users/{user_id}", authenticated=True)

    def list_user_tasks(self, user_id: int) -> list[Task]:
        response = self._http.request("GET", f"/users/{user_id}/todos")
        return [Task.model_validate(item) for item in response.json()]

    def create_task(self, user_id: int, data: TaskCreate) -> Task:
        response = self._http.request(
            "POST", f"/users/{user_id}/todos", json=_dump(data), authenticated=True
        )
        return Task.model_validate(response.json())

    def complete_task(self, task_id: int) -> Task:
        response = self._http.request(
            "PATCH",
            f"/todos/{task_id}",
            json={"status": TaskStatus.completed.value},
            authenticated=True,
        )
        return Task.model_validate(response.json())

    def delete_task(self, task_id: int) -> None:
        self._http.request("DELETE", f"/todos/{task_id}", authenticated=True)


def _dump(model: UserCreate | TaskCreate) -> dict[str, Any]:
    # mode="json" turns enums into their values and datetimes into ISO strings,
    # which is what GoREST expects on the wire.
    return model.model_dump(mode="json", exclude_none=True)

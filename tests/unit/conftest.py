from collections.abc import Callable
from dataclasses import dataclass

import httpx
import pytest

from retail_client.config import RetryPolicy
from retail_client.http import HttpExecutor


@dataclass
class ExecutorSetup:
    executor: HttpExecutor
    delays: list[float]


HandlerItem = httpx.Response | Exception
ExecutorFactory = Callable[..., ExecutorSetup]


class RecordingSleep:
    def __init__(self) -> None:
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


@pytest.fixture
def make_executor() -> ExecutorFactory:
    def factory(
        responses: list[HandlerItem],
        retry: RetryPolicy | None = None,
        token: str | None = "test-token",
    ) -> ExecutorSetup:
        queue = list(responses)

        def handler(request: httpx.Request) -> httpx.Response:
            # request is needed because of httpx library contract
            item = queue.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

        client = httpx.Client(base_url="https://api.test", transport=httpx.MockTransport(handler))
        recorder = RecordingSleep()
        executor = HttpExecutor(client, retry or RetryPolicy(), token=token, sleep=recorder)
        return ExecutorSetup(executor=executor, delays=recorder.delays)

    return factory

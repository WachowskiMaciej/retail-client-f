from collections.abc import Callable

import httpx
import pytest

from retail_client.config import RetryPolicy
from retail_client.http import HttpExecutor

HandlerItem = httpx.Response | Exception
ExecutorFactory = Callable[..., tuple[HttpExecutor, list[float]]]


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
    ) -> tuple[HttpExecutor, list[float]]:
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
        return executor, recorder.delays

    return factory

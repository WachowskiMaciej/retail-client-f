import time
from collections.abc import Callable
from typing import Any

import httpx

from .config import RetryPolicy
from .errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    RequestTimeoutError,
    ServerError,
    TransportError,
    ValidationError,
)


class HttpExecutor:
    def __init__(
        self,
        client: httpx.Client,
        retry: RetryPolicy,
        token: str | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client
        self._retry = retry
        self._token = token
        self._sleep = sleep

    def request(
        self,
        method: str,
        path: str,
        json: Any = None,
        params: dict[str, Any] | None = None,
        authenticated: bool = False,
    ) -> httpx.Response:
        headers = self._auth_headers(authenticated)

        last_exc: Exception | None = None

        for attempt in range(1, self._retry.max_attempts + 1):
            try:
                response = self._client.request(
                    method, path, json=json, params=params, headers=headers
                )
            except httpx.TimeoutException:
                last_exc = RequestTimeoutError(f"request to {path} timed out")
                if attempt < self._retry.max_attempts:
                    self._sleep(self._retry.delay_seconds)
                continue
            except httpx.TransportError as exc:
                last_exc = TransportError(f"could not reach {path}: {exc}")
                if attempt < self._retry.max_attempts:
                    self._sleep(self._retry.delay_seconds)
                continue

            if self._should_retry(response.status_code) and attempt < self._retry.max_attempts:
                self._sleep(self._retry.delay_seconds)
                continue
            if response.is_success:
                return response
            raise self._map_to_error(response)

        assert last_exc is not None
        raise last_exc

    def _auth_headers(self, authenticated: bool) -> dict[str, str]:
        if not authenticated:
            return {}
        if not self._token:
            raise AuthenticationError(
                401, "this operation requires a token but none was configured"
            )
        return {"Authorization": f"Bearer {self._token}"}

    def _should_retry(self, status_code: int) -> bool:
        return status_code in self._retry.retry_statuses

    def _map_to_error(self, response: httpx.Response) -> APIError:
        status = response.status_code
        details = _safe_json_return(response)
        message = _extract_message(details) or response.reason_phrase or "request failed"

        if status == 401:
            return AuthenticationError(status, message, details=details)
        if status == 404:
            return NotFoundError(status, message, details=details)
        if status == 422:
            return ValidationError(status, message, details=details)
        if status == 429:
            return RateLimitError(status, message, details=details)
        if status >= 500:
            return ServerError(status, message, details=details)
        return APIError(status, message, details=details)


def _safe_json_return(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _extract_message(details: Any) -> str | None:
    if isinstance(details, dict):
        message = details.get("message")
        if isinstance(message, str):
            return message
    # GoREST validation errors arrive as [{"field": ..., "message": ...}].
    if isinstance(details, list) and details:
        first = details[0]
        if isinstance(first, dict) and {"field", "message"}.issubset(first):
            return f"{first['field']} {first['message']}"
    return None

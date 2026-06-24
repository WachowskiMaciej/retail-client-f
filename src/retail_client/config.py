"""Client configuration."""

import os
from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://gorest.co.in/public/v2"
DEFAULT_TIMEOUT = 10.0


@dataclass(frozen=True)
class RetryPolicy:
    # Retry rate limiting and transient 5xx; wait a fixed delay between tries.
    # Other 4xx are never retried - they won't fix themselves.
    max_attempts: int = 3
    delay_seconds: float = 1.0
    retry_statuses: frozenset[int] = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class ClientConfig:
    base_url: str = DEFAULT_BASE_URL
    token: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    retry: RetryPolicy = field(default_factory=RetryPolicy)

    @classmethod
    def from_env(cls) -> "ClientConfig":
        timeout_raw = os.environ.get("GOREST_TIMEOUT")
        return cls(
            base_url=os.envirClientConfigon.get("GOREST_BASE_URL", DEFAULT_BASE_URL),
            token=os.environ.get("GOREST_TOKEN"),
            timeout=float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT,
        )

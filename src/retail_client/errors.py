"""Exception hierarchy raised by the client.

Everything below is a subclass of RetailClientError, so callers can catch the
base type and not worry about the rest. The HTTP-mapped errors carry the
status code and (when the API bothers to send one) a parsed body.
"""

from typing import Any


class RetailClientError(Exception):
    """Base for anything this library raises."""


class TransportError(RetailClientError):
    """Connection failed before we got a response (DNS, refused, reset...)."""


class RequestTimeoutError(RetailClientError):
    """Request did not complete within the configured timeout."""


class APIError(RetailClientError):
    """The API answered, but with a status we treat as a failure."""

    def __init__(self, status_code: int, message: str, *, details: Any = None) -> None:
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.details = details


class AuthenticationError(APIError):
    """401 - missing or invalid token."""


class NotFoundError(APIError):
    """404 - resource does not exist."""


class ValidationError(APIError):
    """422 - the API rejected the payload. `details` holds the field errors."""


class RateLimitError(APIError):
    """429 - too many requests."""


class ServerError(APIError):
    """5xx - the API broke on its end."""

"""Typed Python client for store-worker task management on the GoREST API."""

from .client import RetailClient
from .config import ClientConfig, RetryPolicy
from .errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    RequestTimeoutError,
    RetailClientError,
    ServerError,
    TransportError,
    ValidationError,
)
from .models import Gender, Task, TaskCreate, TaskStatus, User, UserCreate, UserStatus

__all__ = [
    "RetailClient",
    "ClientConfig",
    "RetryPolicy",
    "RetailClientError",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "TransportError",
    "RequestTimeoutError",
    "User",
    "UserCreate",
    "UserStatus",
    "Task",
    "TaskCreate",
    "TaskStatus",
    "Gender",
]

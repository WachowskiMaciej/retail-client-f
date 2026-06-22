"""Typed models for the two resources we wrap: store workers (users) and
their tasks (todos).

The `*Create` models are the input side - what a caller hands us. The plain
models are the output side - what the API hands back, including server-set
fields like `id`.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Gender(StrEnum):
    male = "male"
    female = "female"


class UserStatus(StrEnum):
    active = "active"
    inactive = "inactive"


class TaskStatus(StrEnum):
    pending = "pending"
    completed = "completed"


class UserCreate(BaseModel):
    name: str
    email: str
    gender: Gender
    status: UserStatus = UserStatus.active


class User(BaseModel):
    id: int
    name: str
    email: str
    gender: Gender
    status: UserStatus


class TaskCreate(BaseModel):
    title: str
    due_on: datetime | None = None
    status: TaskStatus = TaskStatus.pending


class Task(BaseModel):
    id: int
    user_id: int
    title: str
    due_on: datetime | None = None
    status: TaskStatus

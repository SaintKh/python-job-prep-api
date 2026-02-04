from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool


class TaskPatch(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    done: Optional[bool] = None


class Task(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime

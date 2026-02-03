from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False

class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool

class Task(TaskCreate):
    id: int

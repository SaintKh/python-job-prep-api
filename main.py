from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="Tasks API")

# --- Models ---
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False

class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool

class Task(TaskCreate):
    id: int


# --- "Database" (in-memory) ---
tasks: List[Task] = []
next_id = 1


# --- Routes ---
@app.get("/")
def read_root():
    return {"message": "Tasks API is running"}


@app.get("/tasks", response_model=List[Task])
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, update: TaskUpdate):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = Task(id=task_id, title=update.title, done=update.done)
            tasks[i] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail="Task not found")




@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task: TaskCreate):
    global next_id
    new_task = Task(id=next_id, title=task.title, done=task.done)
    tasks.append(new_task)
    next_id += 1
    return new_task

from fastapi import APIRouter, HTTPException, status
from typing import List

from ..schemas import Task, TaskCreate, TaskUpdate, TaskPatch
from ..db import tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[Task])
def list_tasks():
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task: TaskCreate):
    # Import next_id lazily so we can update it
    from .. import db

    new_task = Task(id=db.next_id, title=task.title, done=task.done)
    tasks.append(new_task)
    db.next_id += 1
    return new_task


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, update: TaskUpdate):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = Task(id=task_id, title=update.title, done=update.done)
            tasks[i] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

@router.patch("/{task_id}", response_model=Task)
def patch_task(task_id: int, patch: TaskPatch):
    # If the client sends an empty body like {}, we should reject it
    if patch.model_dump(exclude_unset=True) == {}:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    for i, task in enumerate(tasks):
        if task.id == task_id:
            updated_data = task.model_dump()
            updated_data.update(patch.model_dump(exclude_unset=True))

            updated_task = Task(**updated_data)
            tasks[i] = updated_task
            return updated_task

    raise HTTPException(status_code=404, detail="Task not found")



@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail="Task not found")

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from typing import List

from ..schemas import Task, TaskCreate, TaskUpdate, TaskPatch
from ..db import tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])

def find_task_index(task_id: int) -> int:
    for i, task in enumerate(tasks):
        if task.id == task_id:
            return i
    raise HTTPException(status_code=404, detail="Task not found")


def ensure_unique_title(title: str, ignore_id: int | None = None) -> None:
    for t in tasks:
        if ignore_id is not None and t.id == ignore_id:
            continue
        if t.title.lower() == title.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task with this title already exists"
            )



@router.get("", response_model=List[Task])
def list_tasks():
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    idx = find_task_index(task_id)
    return tasks[idx]



@router.post("", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task: TaskCreate):
    from .. import db
    from datetime import datetime, timezone

    ensure_unique_title(task.title)

    now = datetime.now(timezone.utc)

    new_task = Task(
        id=db.next_id,
        title=task.title,
        done=task.done,
        created_at=now,
        updated_at=now
    )

    tasks.append(new_task)
    db.next_id += 1

    return new_task




@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, update: TaskUpdate):
    from datetime import datetime, timezone

    idx = find_task_index(task_id)

    ensure_unique_title(update.title, ignore_id=task_id)

    task = tasks[idx]

    updated_task = Task(
        id=task_id,
        title=update.title,
        done=update.done,
        created_at=task.created_at,
        updated_at=datetime.now(timezone.utc)
    )

    tasks[idx] = updated_task
    return updated_task


@router.patch("/{task_id}", response_model=Task)
def patch_task(task_id: int, patch: TaskPatch):
    from datetime import datetime, timezone

    if patch.model_dump(exclude_unset=True) == {}:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    idx = find_task_index(task_id)

    patch_data = patch.model_dump(exclude_unset=True)

    if "title" in patch_data:
        ensure_unique_title(patch_data["title"], ignore_id=task_id)

    task = tasks[idx]

    updated_data = task.model_dump()
    updated_data.update(patch_data)
    updated_data["updated_at"] = datetime.now(timezone.utc)

    updated_task = Task(**updated_data)
    tasks[idx] = updated_task

    return updated_task



@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    idx = find_task_index(task_id)
    tasks.pop(idx)
    return


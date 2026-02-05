from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas import Task, TaskCreate, TaskUpdate, TaskPatch
from ..database import get_db
from .. import models

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[Task])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.Task)
        .filter(models.Task.title.ilike(task.title))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task with this title already exists",
        )

    now = datetime.now(timezone.utc)
    db_task = models.Task(
        title=task.title,
        done=task.done,
        created_at=now,
        updated_at=now,
    )

    db.add(db_task)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task with this title already exists",
        )

    db.refresh(db_task)  # ✅ refresh the ORM instance
    return db_task




@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Duplicate title check (case-insensitive), ignoring this task
    duplicate = (
        db.query(models.Task)
        .filter(models.Task.id != task_id)
        .filter(models.Task.title.ilike(update.title))
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task with this title already exists",
        )

    task.title = update.title
    task.done = update.done
    task.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task with this title already exists",
        )

    db.refresh(task)
    return task



@router.patch("/{task_id}", response_model=Task)
def patch_task(task_id: int, patch: TaskPatch, db: Session = Depends(get_db)):
    patch_data = patch.model_dump(exclude_unset=True)

    # Reject completely empty PATCH body
    if patch_data == {}:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # If title is provided, check duplicates (case-insensitive), ignoring this task
    if "title" in patch_data:
        duplicate = (
            db.query(models.Task)
            .filter(models.Task.id != task_id)
            .filter(models.Task.title.ilike(patch_data["title"]))
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task with this title already exists",
            )
        task.title = patch_data["title"]

    if "done" in patch_data:
        task.done = patch_data["done"]

    task.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task with this title already exists",
        )

    db.refresh(task)
    return task



@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return

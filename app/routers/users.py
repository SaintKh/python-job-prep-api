from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import models
from ..schemas import User, UserCreate
from ..database import get_db
from ..security import hash_password

router = APIRouter(tags=["users"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User)
        .filter(models.User.username == user.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    db_user = models.User(
        username=user.username,
        hashed_password=hash_password(user.password),
    )

    db.add(db_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    db.refresh(db_user)
    return db_user
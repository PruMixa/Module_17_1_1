from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from sqlalchemy import insert, update, delete, select
from app.schemas import CreateUser, UpdateUser

from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id")
async def user_by_id(db: Annotated[Session, Depends(get_db)],
                     user_id: int):
    users = db.scalar(select(User).where(User.id == user_id))
    if users is not None:
        return users
    raise HTTPException(status_code=404, detail="User was not found")

@router.get("/user_id/tasks")
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id))
    return tasks


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)],
                      user_create: CreateUser):
    db.execute(insert(User).values(username=user_create.username,
                                   firstname=user_create.firstname,
                                   lastname=user_create.lastname,
                                   age=user_create.age,
                                   slug=slugify(user_create.username)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int,
                      user_update: UpdateUser):
    users = db.scalars(select(User).where(User.id == user_id))
    for u in users:
        if u is not None:
            db.execute(update(User).where(User.id == user_id).values(
                firstname=user_update.firstname,
                lastname=user_update.lastname,
                age=user_update.age))
            db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'User update is successful'
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')


@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')

    db.execute(delete(Task).where(Task.user_id == user_id))

    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful'
    }
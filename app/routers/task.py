from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from sqlalchemy import insert, update, delete, select
from app.schemas import CreateTask, UpdateTask

from slugify import slugify

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/")
async def all_task(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get("/task_id")
async def tsk_by_id(db: Annotated[Session, Depends(get_db)],
                    task_id: int):
    tasks = db.scalars(select(Task).where(Task.id == task_id))
    if tasks is not None:
        return tasks
    raise HTTPException(status_code=404, detail="Task was not found")


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], create_task: CreateTask, user_id: int):
    users = db.scalar(select(User).where(User.id == user_id))
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found")

    db.execute(insert(Task).values(title=create_task.title,
                                   content=create_task.content,
                                   priority=create_task.priority,
                                   user_id=user_id,
                                   slug=slugify(create_task.title)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Task create is successful!'}


@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int,
                      task_update: UpdateTask):
    tasks = db.scalars(select(Task).where(Task.id == task_id))
    for u in tasks:
        if u is not None:
            db.execute(update(Task).where(Task.id == task_id).values(
                title=task_update.title,
                content=task_update.content,
                priority=task_update.priority))
            db.commit()
            return {
                'status code': status.HTTP_200_OK,
                'transaction': 'Task update is successful'
            }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')


@router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int):
    tasks = db.scalars(select(Task).where(Task.id == task_id))
    for u in tasks:
        if u is not None:
            db.execute(delete(Task).where(Task.id == task_id))
            db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Task delete is successful'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')

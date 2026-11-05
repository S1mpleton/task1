from typing import List, Tuple, Optional

from fastapi import HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.schemas.tasks import CreateTask
from domain.tasks import TaskStatus, decode_cursor, encode_cursor
from infrastructure.database.models.task import Task
from infrastructure.database.repositories import tasks as task_repo



def create_task(
        session: Session,
        task_data: CreateTask,
        owner_id: int,
) -> Task:
    task = Task(
        owner_id=owner_id,
        **task_data.model_dump()
    )

    try:
        task_repo.create_task(session, task)
        session.commit()
        session.refresh(task)

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task violates a database constraint",
        )

    except SQLAlchemyError:
        session.rollback()
        raise

    return task


def get_task(
    session: Session,
    task_id: int,
    owner_id: int,
) -> Task:

    task = task_repo.get_task(
        session=session,
        task_id=task_id,
        owner_id=owner_id,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task

def get_tasks(
        session: Session,
        owner_id: int,
        limit: int = 20,
        offset: int = 0,
        sample_status: TaskStatus | None = None,
) -> List[Task]:
    tasks = task_repo.get_tasks(
        session=session,
        owner_id=owner_id,
        limit=limit,
        offset=offset,
        sample_status=sample_status
    )

    return tasks

def get_tasks_by_cursor(
        session: Session,
        owner_id: int,
        limit: int = 20,
        cursor_task_data: str | None = None,
        task_status: TaskStatus | None = None,
) -> Tuple[List[Task], Optional[str]]:
    cursor_task = None if cursor_task_data is None else decode_cursor(cursor_task_data)

    tasks = task_repo.get_tasks_by_cursor(
        session=session,
        owner_id=owner_id,
        limit=limit,
        cursor_task=cursor_task,
        task_status=task_status
    )

    has_next = len(tasks) > limit
    page_tasks = tasks[:limit]
    next_cursor = None

    if has_next:
        last_task = page_tasks[-1]

        next_cursor = encode_cursor(
            created_at=last_task.created_at,
            task_id=last_task.id
        )

    return page_tasks, next_cursor

def delete_task(
        session: Session,
        owner_id: int,
        task_id: int
) -> None:
    try:
        task = get_task(session, task_id, owner_id)

        task_repo.delete_task(session, task)
        session.commit()

    except SQLAlchemyError:
        session.rollback()
        raise


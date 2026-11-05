from typing import List

from sqlmodel import Session, select, or_, and_

from domain.tasks import TaskStatus, CursorTask
from infrastructure.database.models.task import Task


def create_task(
        session: Session,
        task: Task,
) -> Task:
    session.add(task)
    session.flush()

    return task

def get_task(
        session: Session,
        task_id: int,
        owner_id: int,
) -> Task | None:

    statement = select(Task).where(
        Task.id == task_id,
        Task.owner_id == owner_id,
    )

    return session.exec(statement).first()


def get_tasks(
        session: Session,
        owner_id: int,
        limit: int = 20,
        offset: int = 0,
        sample_status: TaskStatus | None = None,
) -> List[Task]:
    statement = select(Task).where(
        Task.owner_id == owner_id
    )

    if sample_status is not None:
        statement = statement.where(
            Task.status == sample_status
        )

    statement = (
        statement
        .order_by(Task.created_at.asc(), Task.id.asc())
        .offset(offset)
        .limit(limit)
    )

    tasks = session.exec(statement).all()

    return list(tasks)


def get_tasks_by_cursor(
        session: Session,
        owner_id: int,
        limit: int = 20,
        cursor_task: CursorTask | None = None,
        task_status: TaskStatus | None = None,
) -> List[Task]:
    statement = select(Task).where(
        Task.owner_id == owner_id
    )

    if task_status is not None:
        statement = statement.where(
            Task.status == task_status
        )

    if cursor_task is not None:
        statement = statement.where(
            or_(
                Task.created_at > cursor_task.created_at,
                and_(
                    Task.created_at == cursor_task.created_at,
                    Task.id > cursor_task.id
                )
            )
        )

    statement = (
        statement
        .order_by(
            Task.created_at.asc(),
            Task.id.asc()
        )
        .limit(limit + 1)
    )

    tasks = session.exec(statement).all()

    return list(tasks)


def delete_task(
        session: Session,
        task: Task,
) -> None:
    session.delete(task)

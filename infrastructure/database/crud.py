from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session, or_, and_

from api.schemas.tasks import CreateTask, ResponseTask, TaskPage, encode_cursor, decode_cursor
from core.security.password import hash_password
from .models import User, Task
from api.schemas.users import CreateUser, ResponseUser
from ..dependencies import TaskStatus


class CRUD:
    # Users
    @classmethod
    def create_user(cls, create_user: CreateUser, session: Session) -> ResponseUser:

        user = User(
            name=create_user.name,
            email=create_user.email,
            password_hash=hash_password(create_user.password)
        )

        session.add(user)
        try:
            session.commit()
            session.refresh(user)

        except IntegrityError as e:
            session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )

        return ResponseUser.model_validate(user)

    @classmethod
    def get_user(cls, user_id: int, session: Session) -> ResponseUser:
        user = session.get(User, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return ResponseUser.model_validate(user)

    @staticmethod
    def get_user_by_email(email: str, session: Session) -> ResponseUser | None:

        statement = select(User).where(
            User.email == email
        )

        response_user = ResponseUser.model_validate(
            session.exec(statement).first()
        )
        return response_user

    @staticmethod
    def get_user_full_by_email(email: str, session: Session) -> User | None:
        statement = select(User).where(
            User.email == email
        )

        return session.exec(statement).first()

    @classmethod
    def delete_user(cls, user_id: int, session: Session) -> None:

        user = session.get(User, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        session.delete(user)
        session.commit()


    # Tasks
    @classmethod
    def create_task(cls, create_task: CreateTask, user_id: int, session: Session) -> ResponseTask:

        task = Task(
            title=create_task.title,
            description=create_task.description,
            status=create_task.status,
            user_id=user_id,
            version=1
        )

        session.add(task)

        try:
            session.commit()
            session.refresh(task)

        except IntegrityError:
            session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not create task"
            )

        return ResponseTask.model_validate(task)

    @classmethod
    def get_task(cls, task_id: int, user_id: int, session: Session) -> ResponseTask:

        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )

        task = session.exec(statement).first()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return ResponseTask.model_validate(task)

    @classmethod
    def get_tasks(
            cls,
            user_id: int,
            session: Session,
            sample_status: TaskStatus | None = None,
            limit: int = 20,
            offset: int = 0
    ) -> list[ResponseTask]:

        statement = select(Task).where(
            Task.user_id == user_id
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

        return [
            ResponseTask.model_validate(task)
            for task in tasks
        ]

    # GPT Code
    @classmethod
    def get_tasks_by_cursor(
            cls,
            user_id: int,
            session: Session,
            task_status: TaskStatus | None = None,
            limit: int = 20,
            cursor: str | None = None
    ) -> TaskPage:

        statement = select(Task).where(
            Task.user_id == user_id
        )

        if task_status is not None:
            statement = statement.where(
                Task.status == task_status
            )

        if cursor is not None:
            cursor_date, cursor_id = decode_cursor(cursor)

            statement = statement.where(
                or_(
                    Task.created_at > cursor_date,
                    and_(
                        Task.created_at == cursor_date,
                        Task.id > cursor_id
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

        has_next = len(tasks) > limit

        page_tasks = tasks[:limit]

        next_cursor = None

        if has_next:
            last_task = page_tasks[-1]

            next_cursor = encode_cursor(
                created_at=last_task.created_at,
                task_id=last_task.id
            )

        return TaskPage(
            items=[
                ResponseTask.model_validate(task)
                for task in page_tasks
            ],
            next_cursor=next_cursor
        )

    @classmethod
    def delete_task(cls, task_id: int, user_id: int, session: Session) -> None:

        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )

        task = session.exec(statement).first()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        try:
            session.delete(task)
            session.commit()

        except Exception:
            session.rollback()
            raise




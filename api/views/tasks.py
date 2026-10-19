from typing import Annotated

from fastapi import Depends, APIRouter, status, Query

from api.schemas.tasks import ResponseTask, CreateTask, TaskPage
from core.jwt.utils import get_current_user_id
from infrastructure.database.crud import CRUD
from infrastructure.database.session import SessionDep
from infrastructure.dependencies import TaskStatus

router = APIRouter()


@router.post("/tasks")
async def create_task(
        task: CreateTask,
        user_id: Annotated[int, Depends(get_current_user_id)],
        session: SessionDep
) -> ResponseTask:
    response_task = CRUD.create_task(task, user_id, session)
    return response_task


@router.get(
    "/tasks",
    description="limit-offset pagination",
    response_model=list[ResponseTask],
)
async def get_tasks(
    user_id: Annotated[int, Depends(get_current_user_id)],
    session: SessionDep,
    task_status: TaskStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0
) -> list[ResponseTask]:

    return CRUD.get_tasks(
        user_id=user_id,
        session=session,
        sample_status=task_status,
        limit=limit,
        offset=offset
    )

@router.get( # GPT Code
    "/pageTasksCursor",
    description="pagination by cursor",
)
async def get_tasks_by_cursor(
    user_id: Annotated[int, Depends(get_current_user_id)],
    session: SessionDep,
    task_status: TaskStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: str | None = None
) -> TaskPage:

    return CRUD.get_tasks_by_cursor(
        user_id=user_id,
        session=session,
        task_status=task_status,
        limit=limit,
        cursor=cursor
    )

@router.get("/tasks/{task_id}")
async def get_task(
        task_id: int,
        user_id: Annotated[int, Depends(get_current_user_id)],
        session: SessionDep
) -> ResponseTask:
    response_task = CRUD.get_task(task_id, user_id, session)
    return response_task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
        task_id: int,
        user_id: Annotated[int, Depends(get_current_user_id)],
        session: SessionDep
) -> None:
    CRUD.delete_task(task_id, user_id, session)


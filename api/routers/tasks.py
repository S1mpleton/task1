from typing import Annotated, List

from fastapi import Depends, APIRouter, status, Query

from api.schemas.tasks import ResponseTask, CreateTask, TaskPage
from core.jwt.validate import ValidateToken
from domain.tasks import TaskStatus
from infrastructure.database.session import SessionDep
from services import tasks as tasks_service


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks📝"],
)


@router.post(
    "/create",
    response_model=ResponseTask
)
async def create_task(
        task_data: CreateTask,
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep
):
    return tasks_service.create_task(session, task_data, user_id)



@router.get(
    "/page",
    description="limit-offset pagination",
    response_model=List[ResponseTask],
)
async def get_tasks(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
        task_status: TaskStatus | None = None,
):
    return tasks_service.get_tasks(session, user_id, limit, offset, task_status)


@router.get(
    "/pageByCursor",
    response_model=TaskPage,
    description="pagination by cursor",
)
async def get_tasks_by_cursor(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        cursor_task_data: str | None = None,
        task_status: TaskStatus | None = None,
):

    tasks_list, cursor = tasks_service.get_tasks_by_cursor(
        session,
        user_id,
        limit,
        cursor_task_data,
        task_status
    )
    return TaskPage(
        tasks=[
            ResponseTask.model_validate(task)
            for task in tasks_list
        ],
        next_cursor=cursor
    )


@router.get(
    "get/{task_id}",
    response_model=ResponseTask
)
async def get_task(
        task_id: int,
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep
):
    return tasks_service.get_task(session, task_id, user_id)


@router.delete(
    "delete/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
        task_id: int,
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep
) -> None:
    tasks_service.delete_task(session, user_id, task_id)



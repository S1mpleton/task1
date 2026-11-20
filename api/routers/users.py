from typing import Annotated

from fastapi import APIRouter, Depends, status

from core.jwt.validate import ValidateToken
from services import users as users_service

from api.schemas.users import ResponseUser, CreateUser
from infrastructure.database.session import SessionDep
from infrastructure.dependencies import FunSources

router = APIRouter(
    prefix="/users",
    tags=["Users💁"],
)

@router.post(
    "/create",
    response_model=ResponseUser,
    description=f"![Animation]({FunSources.bebebe})"
)
async def create_user(
        user_data: CreateUser,
        session: SessionDep
):
    return users_service.create_user(session, user_data)


@router.get(
    "get/me",
    response_model=ResponseUser)
async def get_me(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep
):
    return users_service.get_user(session, user_id)


@router.delete(
    "/delete/me",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep
) -> None:
    users_service.delete_user(session, user_id)


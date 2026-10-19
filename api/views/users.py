from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from core.jwt.utils import create_access_token, get_current_user_id
from infrastructure.database.crud import CRUD

from api.schemas.users import ResponseUser, CreateUser, TokenData
from infrastructure.database.session import SessionDep
from services.auth import AuthService

router = APIRouter()


@router.post("/login")
async def login(
        # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        username: Annotated[str, Form()],
        password: Annotated[SecretStr, Form()],
        session: SessionDep
) -> TokenData:

    user = AuthService.authenticate_user(
        email=username,
        password=password.get_secret_value(),
        session=session
    )

    token = create_access_token(user_id=user.id)

    return TokenData(
        access_token=token,
        token_type="bearer",
    )


@router.post("/users", response_model=ResponseUser)
async def create_user(
        user: CreateUser,
        session: SessionDep
):
    user = CRUD.create_user(user, session)
    return user


@router.get("/users", response_model=ResponseUser)
async def get_users(
        user_id: Annotated[int, Depends(get_current_user_id)],
        session: SessionDep
):
    user = CRUD.get_user(user_id, session)
    return user


from typing import Annotated

from fastapi import Form, APIRouter, HTTPException, status
from pydantic import SecretStr

from core.jwt.utils import create_access_token

from api.schemas.users import TokenData
from infrastructure.database.session import SessionDep
from services.auth import AuthService


router = APIRouter(
    prefix="/login",
    tags=["Auth🔐"],
)


@router.post(
    "",
    response_model=TokenData
)
async def login(
        username: Annotated[str, Form()],
        password: Annotated[SecretStr, Form()],
        session: SessionDep
):

    user = AuthService.authenticate_user(
        email=username,
        password=password.get_secret_value(),
        session=session
    )

    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    token = create_access_token(user_id=user.id)

    return TokenData(
        access_token=token,
        token_type="bearer",
    )
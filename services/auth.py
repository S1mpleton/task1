from fastapi import HTTPException, status
from sqlmodel import Session

from infrastructure.database.crud import CRUD
from infrastructure.database.models import User

from core.security.password import verify_password


class AuthService:

    @staticmethod
    def authenticate_user(
        email: str,
        password: str,
        session: Session
    ) -> User:

        user = CRUD.get_user_full_by_email(
            email=email,
            session=session,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
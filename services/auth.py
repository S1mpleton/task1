from fastapi import HTTPException, status
from sqlmodel import Session

from core.security.password import verify_password
from infrastructure.database.models.user import User

from infrastructure.database.repositories import users as users_repo


class AuthService:

    @staticmethod
    def authenticate_user(
        email: str,
        password: str,
        session: Session
    ) -> User:

        user = users_repo.get_user_by_email(session, email)

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
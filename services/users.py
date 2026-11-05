from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from api.schemas.users import CreateUser
from core.security.password import hash_password
from infrastructure.database.models.user import User

from infrastructure.database.repositories import users as user_repo

def create_user(
    session: Session,
    user_data: CreateUser,
) -> User:

    user = User(
        nickname=user_data.nickname,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    try:
        user_repo.create_user(session, user)
        session.commit()
        session.refresh(user)

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    except SQLAlchemyError:
        session.rollback()
        raise

    return user

def get_user(
    session: Session,
    user_id: int,
) -> User:
    user = user_repo.get_user(session, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

def delete_user(
        session: Session,
        user_id: int,
) -> None:
    try:
        user = user_repo.get_user(session, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user_repo.delete_user(session, user)
        session.commit()

    except SQLAlchemyError:
        session.rollback()
        raise





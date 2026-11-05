from pydantic import EmailStr
from sqlmodel import Session, select

from infrastructure.database.models.user import User


def create_user(
        session: Session,
        user: User,
) -> User:
    session.add(user)
    session.flush()

    return user

def get_user(
        session: Session,
        user_id: int,
) -> User | None:
    statement = select(User).where(
        User.id == user_id
    )

    return session.exec(statement).first()


def get_user_by_email(
        session: Session,
        email: str,
) -> User | None:
    statement = select(User).where(
        User.email == email
    )

    return session.exec(statement).first()

def delete_user(
        session: Session,
        user: User
) -> None:
    session.delete(user)

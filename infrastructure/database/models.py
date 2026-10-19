from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from ..dependencies import TaskStatus



class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str = Field(index=True)
    name: str = Field(index=True)
    password_hash: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key='user.id')

    title: str = Field(index=True)
    description: str = Field()
    status: TaskStatus = Field(default=TaskStatus.TODO)
    version: int = Field(default=1)

    start_date: str | None = Field(default=None, index=True)
    end_date: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

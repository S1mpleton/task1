from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, Relationship

from ..dependencies import TaskStatus, FileStatus


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str = Field(index=True)
    name: str = Field(index=True)
    password_hash: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    files: list["File"] = Relationship(back_populates="owner")

class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    owner_id: int = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
    )

    filename: str = Field(max_length=255)

    object_key: str = Field(
        max_length=1024,
        unique=True,
        index=True,
    )

    content_type: str = Field(max_length=255)

    size: int = Field(ge=0)
    status: FileStatus = Field(default=FileStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    owner: User | None = Relationship(back_populates="files")

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

from datetime import datetime, timezone

from sqlmodel import SQLModel, Field

from domain.tasks import TaskStatus


class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    owner_id: int = Field(foreign_key='user.id')

    title: str = Field(index=True)
    description: str = Field()
    status: TaskStatus = Field(default=TaskStatus.TODO)
    version: int = Field(default=1)

    start_date: str | None = Field(default=None, index=True)
    end_date: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
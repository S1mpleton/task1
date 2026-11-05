from datetime import datetime, timezone

from sqlmodel import SQLModel, Field

from infrastructure.dependencies import FileStatus


class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    owner_id: int = Field(foreign_key="user.id", index=True, nullable=False)

    filename: str = Field(max_length=255)
    object_key: str = Field(max_length=1024, unique=True, index=True)
    content_type: str = Field(max_length=255)
    size: int = Field(ge=0)

    status: FileStatus = Field(default=FileStatus.PENDING)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

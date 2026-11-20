from datetime import datetime, timezone

from sqlmodel import SQLModel, Field

from domain.files import UploadStatus


class UploadSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    file_id: int = Field(foreign_key="files.id", unique=True, index=True)

    upload_id: str

    status: UploadStatus = Field(default=UploadStatus.IN_PROGRESS)

    part_size: int = Field(ge=8*1024*1024, default=8*1024*1024) # 8 MiB

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    completed_at: datetime | None = None

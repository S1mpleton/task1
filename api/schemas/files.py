from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from infrastructure.dependencies import FileStatus


class FileCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(max_length=255)
    size: int = Field(gt=0)


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    size: int
    status: FileStatus
    created_at: datetime
    updated_at: datetime
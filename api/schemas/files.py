from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from domain.files import FileStatus



class FileUploadInitRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(max_length=255)
    size: int = Field(gt=0)

class FileUploadInitResponse(BaseModel):
    file_id: int
    put_url: str
    expired_at: int


class FileMultipartUploadInitResponse(BaseModel):
    file_id: int
    upload_id: str

class FileMultipartUploadResponse(BaseModel):
    part_number: int
    upload_url: str



class FileDownloadResponse(BaseModel):
    download_url: str
    expired_at: datetime

class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    size: int
    status: FileStatus
    created_at: datetime
    updated_at: datetime
    uploaded_at: datetime | None
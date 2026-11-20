from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.schemas.files import FileDownloadResponse, FileResponse, \
    FileUploadInitRequest, FileUploadInitResponse, FileMultipartUploadInitResponse, FileMultipartUploadResponse
from core.jwt.validate import ValidateToken
from infrastructure.database.session import SessionDep
from infrastructure.dependencies import FunSources
from infrastructure.storage.config import EXPIRES_IN
from infrastructure.storage.getter import S3StorageDep
from services import files as file_service

router = APIRouter(
    prefix="/files",
    tags=["Files🗒️"],
)

@router.post(
    "/upload",
    response_model=FileUploadInitResponse,
    description=f"![Animation]({FunSources.six_seven})"
)
async def upload_file(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        storage: S3StorageDep,
        upload_init_request: FileUploadInitRequest
):
    file, upload_str = file_service.upload_file(
        session=session,
        storage=storage,
        owner_id=user_id,
        file_name=upload_init_request.file_name,
        content_type=upload_init_request.content_type,
        size=upload_init_request.size,
    )

    file_id = file.id # for PyCharm warning

    if file_id is None:
        raise RuntimeError("File ID was not generated")

    return FileUploadInitResponse(
        file_id=file_id,
        put_url=upload_str,
        expired_at=300
    )

@router.post(
    "/upload/initMultipart",
    response_model=FileMultipartUploadInitResponse,
    description=f"![Animation]({FunSources.six_seven})"
)
async def init_upload_multipart_file(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        storage: S3StorageDep,
        upload_init_request: FileUploadInitRequest
):
    file, upload_id = file_service.init_upload_multipart_file(
        session=session,
        storage=storage,
        owner_id=user_id,
        file_name=upload_init_request.file_name,
        content_type=upload_init_request.content_type,
        size=upload_init_request.size,
    )

    file_id = file.id  # for PyCharm warning

    if file_id is None:
        raise RuntimeError("File ID was not generated")

    return FileMultipartUploadInitResponse(
        file_id=file_id,
        upload_id=upload_id
    )

@router.post(
    "/upload/part",
    response_model=FileMultipartUploadResponse,
    description=f"![Animation]({FunSources.six_seven})"
)
async def upload_part_file(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        storage: S3StorageDep,
        file_id: Annotated[int, Query(...)],
        part_number: Annotated[int, Query(ge=1, le=10000)],
):
    upload_url = file_service.upload_part_file(
        session=session,
        storage=storage,
        file_id=file_id,
        owner_id=user_id,
        part_number=part_number,
    )

    return FileMultipartUploadResponse(
        part_number=part_number,
        upload_url=upload_url,
    )


@router.post(
    "/complete",
    response_model=FileResponse,
)
async def complete_upload_file(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        storage: S3StorageDep,
        file_id: Annotated[int, Query(...)],
):
    file = file_service.complete_single_upload_file(
        session=session,
        storage=storage,
        owner_id=user_id,
        file_id=file_id,
    )

    return FileResponse.model_validate(file)

@router.post(
    "/complete-multipart",
    response_model=FileResponse,
)
def complete_upload_multipart_file(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        storage: S3StorageDep,
        file_id: Annotated[int, Query(...)],
):
    file = file_service.complete_multipart_upload_file(
        session=session,
        storage=storage,
        owner_id=user_id,
        file_id=file_id,
    )

    return FileResponse.model_validate(file)


@router.get(
    "/download",
    response_model=FileDownloadResponse,
)
async def download_file(
        user_id: Annotated[int, Depends(ValidateToken())],
        session: SessionDep,
        storage: S3StorageDep,
        file_id: Annotated[int, Query(...)],
):
    download_url = file_service.get_download_url_file(
        session=session,
        storage=storage,
        owner_id=user_id,
        file_id=file_id
    )

    created_at = datetime.now(tz=timezone.utc)

    return FileDownloadResponse(
        download_url=download_url,
        expired_at=created_at + timedelta(seconds=EXPIRES_IN),
    )






from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from botocore.exceptions import ClientError, BotoCoreError
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from domain.files import FileStatus, UploadStatus, validate_multipart_parts
from infrastructure.database.models.file import File
from infrastructure.database.models.upload_session import UploadSession
from infrastructure.database.repositories import files as file_repo
from infrastructure.database.repositories import upload_sessions as upload_sessions_repo
from infrastructure.storage.s3 import S3Storage


def registry_file_upload(
        session: Session,
        owner_id: int,
        file_name: str,
        content_type: str,
        size: int,
) -> File:
    file = File(
        owner_id=owner_id,
        filename=file_name,
        status=FileStatus.PENDING,
        content_type=content_type,
        object_key=f"{owner_id}/{uuid4().hex}",
        size=size
    )

    try:
        file_repo.create_file(session, file)
        session.commit()
        session.refresh(file)

    except SQLAlchemyError:
        session.rollback()
        raise

    return file


def upload_file(
        session: Session,
        storage: S3Storage,
        owner_id: int,
        file_name: str,
        content_type: str,
        size: int,
) -> tuple[File, str]:
    file = registry_file_upload(
        session=session,
        owner_id=owner_id,
        file_name=file_name,
        content_type=content_type,
        size=size
    )

    upload_url = storage.generate_upload_url(
        object_key=file.object_key,
        content_type=file.content_type
    )

    return file, upload_url

def init_upload_multipart_file(
        session: Session,
        storage: S3Storage,
        owner_id: int,
        file_name: str,
        content_type: str,
        size: int,
) -> tuple[File, UploadSession]:
    file = registry_file_upload(
        session=session,
        owner_id=owner_id,
        file_name=file_name,
        content_type=content_type,
        size=size
    )

    upload_id = storage.initiate_multipart(
        object_key=file.object_key,
        content_type=file.content_type
    )

    try:
        upload_session = upload_sessions_repo.create_upload_session(
            session=session,
            file_id=file.id, #  raise RuntimeError("File ID was not generated")
            upload_id=upload_id,
        )
        session.commit()

    except SQLAlchemyError:
        session.rollback()

        try:
            storage.abort_multipart(
                object_key=file.object_key,
                upload_id=upload_id,
            )
        except Exception:
            print("---Failed to abort multipart upload---")

        raise

    return file, upload_session


def upload_part_file(
    session: Session,
    storage: S3Storage,
    file_id: int,
    owner_id: int,
    part_number: int,
) -> str:

    file = get_file(
        session=session,
        file_id=file_id,
        owner_id=owner_id,
    )

    if file.status != FileStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File is not pending",
        )

    upload_session = upload_sessions_repo.get_active_upload_session(
        session=session,
        file_id=file_id,
    )

    if upload_session is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Active multipart upload not found",
        )

    if not 1 <= part_number <= 10000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid part number",
        )

    if upload_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active multipart upload expired",
        )

    return storage.generate_part_upload_url(
        object_key=file.object_key,
        upload_id=upload_session.upload_id,
        part_number=part_number,
    )


def complete_single_upload_file(
        session: Session,
        storage: S3Storage,
        owner_id: int,
        file_id: int,

) -> File:
    file = file_repo.get_file(
        session=session,
        file_id=file_id,
        owner_id=owner_id
    )

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if file.status == FileStatus.READY:
        return file

    if file.status != FileStatus.PENDING:
        raise HTTPException(
            status_code=409,
            detail="File cannot be completed",
        )

    # Is file exist?
    try:
        object_info = storage.get_object_info(
            file.object_key
        )

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")

        if error_code in ("404", "NoSuchKey", "NotFound"):
            raise HTTPException(
                status_code=409,
                detail="File has not been uploaded yet",
            )

        raise HTTPException(
            status_code=503,
            detail="Storage is temporarily unavailable",
        )

    except BotoCoreError:
        raise HTTPException(
            status_code=503,
            detail="Storage is temporarily unavailable",
        )

    # Is size correct?
    actual_size = object_info["ContentLength"]

    if actual_size != file.size:
        file.status = FileStatus.FAILED

        try:
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise

        raise HTTPException(
            status_code=422,
            detail="File size mismatch",
        )

    # Is content type correct?
    if object_info.get("ContentType") != file.content_type:
        file.status = FileStatus.FAILED

        try:
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise

        raise HTTPException(
            status_code=422,
            detail="Content type mismatch",
        )

    # File is OK
    file.status = FileStatus.READY

    try:
        session.commit()
        session.refresh(file)

    except SQLAlchemyError:
        session.rollback()
        raise

    return file

def complete_multipart_upload_file(
    session: Session,
    storage: S3Storage,
    owner_id: int,
    file_id: int,
) -> File:

    file = get_file(
        session=session,
        owner_id=owner_id,
        file_id=file_id,
    )

    upload = upload_sessions_repo.get_by_file_id(
        session=session,
        file_id=file_id,
    )

    if upload is None:
        raise HTTPException(
            status_code=409,
            detail="Multipart upload not found",
        )

    # Maybe multipart upload already finished
    if (
        file.status == FileStatus.READY
        and upload.status == UploadStatus.COMPLETED
    ):
        return file

    # User is blunt
    if upload.status == UploadStatus.COMPLETING:

        if verify_completed_object(storage, file):
            return mark_multipart_completed(
                session, file, upload
            )

        raise HTTPException(
            status_code=409,
            detail="Upload completion is in progress",
        )

    if (
        file.status != FileStatus.PENDING
        or upload.status != UploadStatus.IN_PROGRESS
    ):
        raise HTTPException(
            status_code=409,
            detail="Multipart upload cannot be completed",
        )

    parts = storage.list_uploaded_parts(
        object_key=file.object_key,
        upload_id=upload.upload_id,
    )

    if not validate_multipart_parts(
        file_size=file.size,
        part_size=upload.part_size,
        parts=parts,
    ):
        raise HTTPException(
            status_code=409,
            detail="Multipart parts are incomplete or invalid",
        )

    # Atomically finish upload
    upload_session_id = upload.id

    if upload_session_id is None:
        raise RuntimeError("Upload session has no ID")

    try:
        claimed = upload_sessions_repo.claim_completion(
            session=session,
            upload_session_id=upload_session_id,
        )

        if not claimed:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Upload is already being completed",
            )

        session.commit()

    except SQLAlchemyError:
        session.rollback()
        raise

    # Build file at MinIO
    storage.complete_multipart(
        object_key=file.object_key,
        upload_id=upload.upload_id,
        parts=parts,
    )

    # Verify result object
    if not verify_completed_object(storage, file):
        raise HTTPException(
            status_code=409,
            detail="Completed object verification failed",
        )

    return mark_multipart_completed(
        session=session,
        file=file,
        upload=upload,
    )

def get_file(
        session: Session,
        owner_id: int,
        file_id: int
) -> File:
    file = file_repo.get_file(
        session=session,
        file_id=file_id,
        owner_id=owner_id
    )

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    return file


def get_ready_file(
        session: Session,
        owner_id: int,
        file_id: int
) -> File:
    file = get_file(
        session=session,
        owner_id=owner_id,
        file_id=file_id
    )

    if file.status != FileStatus.READY:
        raise HTTPException(
            status_code=409,
            detail="File cannot be completed",
        )

    return file


def get_download_url_file(
        session: Session,
        storage: S3Storage,
        owner_id: int,
        file_id: int
) -> str:
    file = get_ready_file(
        session=session,
        owner_id=owner_id,
        file_id=file_id
    )

    return storage.generate_download_url(
        object_key=file.object_key,
    )

def mark_multipart_completed(
    session: Session,
    file: File,
    upload: UploadSession,
) -> File:

    now = datetime.now(timezone.utc)

    file.status = FileStatus.READY
    file.uploaded_at = now
    file.updated_at = now

    upload.status = UploadStatus.COMPLETED
    upload.completed_at = now

    try:
        session.add(file)
        session.add(upload)
        session.commit()
        session.refresh(file)
    except SQLAlchemyError:
        session.rollback()
        raise

    return file


def verify_completed_object(
    storage: S3Storage,
    file: File,
) -> bool:

    if not storage.object_exists(file.object_key):
        return False

    info = storage.get_object_info(file.object_key)

    return (
        info["ContentLength"] == file.size
        and info.get("ContentType") == file.content_type
    )



from datetime import datetime, timezone, timedelta

from sqlalchemy import update
from sqlmodel import Session, select, desc, col

from domain.files import UploadStatus, EXPIRE_UPLOAD_SESSION_HOURS
from infrastructure.database.models.upload_session import UploadSession


def create_upload_session(
        session: Session,
        file_id: int,
        upload_id: str,
) -> UploadSession:

    datetime_now = datetime.now(timezone.utc)

    upload_session = UploadSession(
        file_id=file_id,
        upload_id=upload_id,
        expires_at = datetime_now + timedelta(hours=EXPIRE_UPLOAD_SESSION_HOURS)
    )

    session.add(upload_session)
    session.flush()

    return upload_session


def get_active_upload_session(
    session: Session,
    file_id: int,
) -> UploadSession | None:

    statement = (
        select(UploadSession)
        .where(
            UploadSession.file_id == file_id,
            UploadSession.status == UploadStatus.IN_PROGRESS,
        )
        .order_by(
            desc(UploadSession.created_at),
            desc(UploadSession.id),
        )
    )

    return session.exec(statement).first()

def get_by_file_id(
    session: Session,
    file_id: int,
) -> UploadSession | None:

    statement = select(UploadSession).where(
        UploadSession.file_id == file_id
    )

    return session.exec(statement).first()


def claim_completion(
    session: Session,
    upload_session_id: int,
) -> bool:

    statement = (
        update(UploadSession)
        .where(
            col(UploadSession.id) == upload_session_id,
            col(UploadSession.status) == UploadStatus.IN_PROGRESS,
        )
        .values(status=UploadStatus.COMPLETING)
        .returning(col(UploadSession.id))
    )

    result = session.exec(statement)

    return result.scalar_one_or_none() is not None
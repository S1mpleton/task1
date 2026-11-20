from sqlmodel import Session, select, desc

from infrastructure.database.models.file import File


def create_file(
    session: Session,
    file: File,
) -> File:
    session.add(file)
    session.flush()

    return file


def get_file(
    session: Session,
    file_id: int,
    owner_id: int,
) -> File | None:
    statement = select(File).where(
        File.id == file_id,
        File.owner_id == owner_id,
    )

    return session.exec(statement).first()


def get_all_files(
    session: Session,
    owner_id: int,
) -> list[File]:

    statement = (
        select(File)
        .where(File.owner_id == owner_id)
        .order_by(
            desc(File.created_at),
            desc(File.id),
        )
    )

    return list(session.exec(statement).all())


def delete_file(
    session: Session,
    file: File,
) -> None:
    session.delete(file)


from enum import Enum

EXPIRE_UPLOAD_SESSION_HOURS = 12

class FileStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class UploadStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETING = "completing"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


# Gpt code
def validate_multipart_parts(
    file_size: int,
    part_size: int,
    parts: list[dict],
) -> bool:

    if file_size <= 0 or part_size <= 0:
        return False

    expected_count = (file_size + part_size - 1) // part_size

    if expected_count > 10000:
        return False

    if len(parts) != expected_count:
        return False

    for index, part in enumerate(parts, start=1):

        if part["PartNumber"] != index:
            return False

        expected_size = min(
            part_size,
            file_size - (index - 1) * part_size,
        )

        if part["Size"] != expected_size:
            return False

    return True
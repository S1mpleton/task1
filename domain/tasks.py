import base64
import json
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from fastapi import HTTPException, status


class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"

class CursorTask(BaseModel):
    id: int = Field(...)
    created_at: datetime = Field(...)

def encode_cursor(created_at: datetime, task_id: int) -> str:
    data = {
        "created_at": created_at.isoformat(),
        "id": task_id
    }

    raw = json.dumps(data).encode("utf-8")

    return base64.urlsafe_b64encode(raw).decode("ascii")

def decode_cursor(cursor: str) -> CursorTask:
    try:
        raw = base64.b64decode(
            cursor.encode("ascii"),
            altchars=b"-_",
            validate=True
        )

        data = json.loads(raw)

        created_at = datetime.fromisoformat(data["created_at"])
        task_id = data["id"]

        if (
            not isinstance(task_id, int)
            or isinstance(task_id, bool)
            or task_id < 1
        ):
            raise ValueError("Invalid task id")

        return CursorTask(
            id=task_id,
            created_at=created_at
        )

    except (ValueError, KeyError, TypeError, UnicodeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid cursor"
        )

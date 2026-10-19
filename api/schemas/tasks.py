import base64
import json
from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from infrastructure.dependencies import TaskStatus


class CreateTask(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    status: TaskStatus = Field(default=TaskStatus.TODO)

class ResponseTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(...) # Maybe use title - user_id unique
    title: str = Field(...)
    description: str = Field(...)
    status: TaskStatus = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)


# GPT Code
def encode_cursor(created_at: datetime, task_id: int) -> str:
    data = {
        "created_at": created_at.isoformat(),
        "id": task_id
    }

    raw = json.dumps(data).encode("utf-8")

    return base64.urlsafe_b64encode(raw).decode("ascii")

def decode_cursor(cursor: str) -> tuple[datetime, int]:
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

        return created_at, task_id

    except (ValueError, KeyError, TypeError, UnicodeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid cursor"
        )

class TaskPage(BaseModel):
    items: list[ResponseTask]
    next_cursor: str | None = None
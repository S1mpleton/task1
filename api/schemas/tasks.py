from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from domain.tasks import TaskStatus


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

class TaskPage(BaseModel):
    tasks: list[ResponseTask]
    next_cursor: str | None = None
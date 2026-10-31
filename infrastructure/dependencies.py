from enum import Enum

class FileStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"

class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
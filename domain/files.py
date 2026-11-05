from enum import Enum


class FileStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"
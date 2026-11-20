from typing import Annotated

from sqlmodel import Session

from fastapi import Depends, Request
from .s3 import S3Storage


# Fast API documentation code
def get_s3_storage(request: Request) -> S3Storage:
    return request.app.state.s3_storage

S3StorageDep = Annotated[
    S3Storage,
    Depends(get_s3_storage),
]
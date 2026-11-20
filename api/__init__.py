from fastapi import APIRouter

from .routers import *

router_api = APIRouter(
    prefix="/api"
)

router_api.include_router(login_router)
router_api.include_router(users_router)
router_api.include_router(tasks_router)
router_api.include_router(files_router)


__all__ = (
    "router_api",
)
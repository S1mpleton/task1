from .login import router as login_router
from .tasks import router as tasks_router
from .users import router as users_router
from .files import router as files_router

__all__ = (
    "login_router",
    "tasks_router",
    "users_router",
    "files_router"
)
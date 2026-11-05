from fastapi import APIRouter


from api.schemas.users import ResponseUser, CreateUser
from infrastructure.database.session import SessionDep
from infrastructure.dependencies import FunSources

router = APIRouter(
    prefix="/files",
    tags=["Files🗒️"],
)

@router.post(
    "",
    response_model=ResponseUser,
    description=f"![Animation]({FunSources.bebebe})"
)
async def create_user(
        user: CreateUser,
        session: SessionDep
):
    user = CRUD.create_user(user, session)
    return user

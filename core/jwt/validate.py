from typing import Annotated

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError

from .utils import decode_jwt
from .config import ACCESS_TOKEN_TYPE, TOKEN_TYPE_FIELD

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

http_bearer = HTTPBearer(auto_error=False)


def check_header_current_token(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    try:
        return decode_jwt(jwt_token=token)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

class ValidateToken:
    def __init__(
            self,
            token_type: str = ACCESS_TOKEN_TYPE,
    ):
        self.token_type = token_type

    async def __call__(
            self,
            payload: Annotated[dict, Depends(check_header_current_token)]
    ) -> int:
        self.validate_token_type(payload, self.token_type)
        sub = payload.get("sub")

        if not isinstance(sub, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        try:
            user_id = int(sub)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    @classmethod
    def validate_token_type(
            cls,
            payload: dict,
            token_type: str
    ) -> None:
        current_type = payload.get(TOKEN_TYPE_FIELD)
        if not current_type == token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
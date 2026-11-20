from pydantic import EmailStr

from .utils import create_jwt
from .config import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, jwt_settings


def get_access_token(
        user_id: int,
        email: EmailStr,
) -> str:
    jwt_payload = {
        "sub": str(user_id),
        "email": email,
    }

    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=jwt_settings.access_token_expire_minutes
    )


def get_refresh_token(
        user_id: int,
        email: EmailStr,
) -> str:
    jwt_payload = {
        "sub": str(user_id),
        "email": email,
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        payload=jwt_payload,
        expire_timedelta=jwt_settings.refresh_token_expire_minutes
    )
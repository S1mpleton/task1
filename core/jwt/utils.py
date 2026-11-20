from datetime import datetime, timezone, timedelta

import jwt

from .config import jwt_settings, TOKEN_TYPE_FIELD

def encode_jwt(
        payload: dict,
        private_key: str = jwt_settings.secret_key,
        algorithm: str = jwt_settings.algorithm,
        expire_minutes: int = jwt_settings.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:
    to_encode = payload.copy()

    now_date_time = datetime.now(tz=timezone.utc)

    if expire_timedelta:
        expire = now_date_time + expire_timedelta
    else:
        expire = now_date_time + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now_date_time
    )
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
        jwt_token: str | bytes,
        public_key: str = jwt_settings.secret_key,
        algorithm: str = jwt_settings.algorithm
) -> dict:
    decoded = jwt.decode(jwt_token, public_key, algorithms=[algorithm])
    return decoded


def create_jwt(
        token_type: str,
        payload: dict,
        expire_minutes: int = jwt_settings.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: token_type
    }

    jwt_payload.update(payload)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )

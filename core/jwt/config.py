from pydantic_settings import BaseSettings, SettingsConfigDict


TOKEN_TYPE_FIELD = "type"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class JWTSettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 42_000

    aws_access_key_id: str
    aws_secret_access_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


jwt_settings = JWTSettings()



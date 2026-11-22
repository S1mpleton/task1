from pydantic_settings import BaseSettings, SettingsConfigDict

EXPIRES_IN = 2200

class S3Settings(BaseSettings):
    s3_endpoint: str
    s3_region: str
    s3_bucket: str

    aws_access_key_id: str
    aws_secret_access_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = S3Settings()
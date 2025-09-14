from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DB_PASSWORD: str
    DB_HOSTNAME: str
    DB_HOST: str
    DB_USER: str
    DB_PORT: str
    DB_TABLE: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    SECRET_KEY: str

    class Config:
        env_file = [".db.env"]
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore

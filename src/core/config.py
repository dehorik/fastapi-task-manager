from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    DATABASE_NAME: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_USER_PASSWORD: str

    ALGORITHM: str
    TOKEN_EXPIRE_MINUTES: float
    TOKEN_SECRET_KEY: str

    MODE: str = "dev"

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_USER_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


settings = Settings()

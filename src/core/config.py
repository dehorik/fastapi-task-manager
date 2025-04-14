from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    DATABASE: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_USER_PASSWORD: str

    ALGORITHM: str
    TOKEN_EXPIRE_MINUTES: int
    TOKEN_SECRET_KEY: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_USER_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE}"

    model_config = SettingsConfigDict(env_file=(BASE_DIR / ".env"))


settings = Settings()

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        async with self.session_maker() as session:
            yield session


database = Database(settings.database_url)

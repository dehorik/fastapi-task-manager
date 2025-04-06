from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .config import settings


class DatabaseHelper:
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


database_helper = DatabaseHelper(settings.database_url)

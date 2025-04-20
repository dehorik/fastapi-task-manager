import pytest
import pytest_asyncio
from alembic.command import upgrade, downgrade
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession

from core import BASE_DIR, DatabaseHelper, settings
from models import Base, User, Group, UsersGroups, Task  # noqa


pytest_plugins = [
    "integration.fixtures",
    "integration.users.fixtures"
]


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    """
    Автоматическая очистка тестовой базы данных и накат миграций в начале
    тестовой сесии, а по завершении сброс базы в первоначальное состояние
    """

    config = Config(BASE_DIR / "alembic.ini")
    config.set_main_option("sqlalchemy.url", settings.database_url)
    downgrade(config, "base")
    upgrade(config, "head")
    yield
    downgrade(config, "base")


@pytest.fixture(scope="session")
def database_helper() -> DatabaseHelper:
    return DatabaseHelper(settings.database_url)


@pytest_asyncio.fixture(scope="function")
async def session(database_helper: DatabaseHelper) -> AsyncSession:
    async with database_helper.session_factory() as session:
        yield session

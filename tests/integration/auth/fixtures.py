import pytest

from auth.auth_service import AuthService
from infrastructure import SQLAlchemyUnitOfWork


@pytest.fixture
def auth_service(unit_of_work: SQLAlchemyUnitOfWork) -> AuthService:
    return AuthService(unit_of_work)

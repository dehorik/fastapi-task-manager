import pytest

from auth.schemas import CredentialsSchema


@pytest.fixture(scope="function")
def fake_credentials_schema() -> CredentialsSchema:
    return CredentialsSchema(
        username="egor",
        password="11111111"
    )

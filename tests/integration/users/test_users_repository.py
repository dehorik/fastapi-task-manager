from uuid import uuid4

import pytest

from exceptions import ResultNotFound
from infrastructure import UsersRepository
from schemas import UserSchema
from .helpers import generate_username


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get(
        users_repository: UsersRepository,
        user_data: UserSchema
) -> None:
    user = await users_repository.get(user_data.user_id)
    assert user
    assert user.user_id == user_data.user_id

    non_existent_user = await users_repository.get(uuid4())
    assert non_existent_user is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_by_username(
        users_repository: UsersRepository,
        user_data: UserSchema
) -> None:
    user = await users_repository.get_user_by_username(user_data.username)
    assert user
    assert user.user_id == user_data.user_id
    assert user.hashed_password

    non_existent_user = await users_repository.get_user_by_username(generate_username())
    assert non_existent_user is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update(
        users_repository: UsersRepository,
        user_data: UserSchema
) -> None:
    data = {"username": generate_username()}
    user_data.username = data["username"]

    user = await users_repository.update(user_data.user_id, data)
    assert user
    user_schema = UserSchema.model_validate(user, from_attributes=True)
    assert user_schema.model_dump() == user_data.model_dump()

    await users_repository.session.flush()
    users_repository.session.expire_all()

    user = await users_repository.update(user_data.user_id, {})
    user_schema = UserSchema.model_validate(user, from_attributes=True)
    assert user_schema.model_dump() == user_data.model_dump()

    with pytest.raises(ResultNotFound):
        await users_repository.update(uuid4(), data)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete(
        users_repository: UsersRepository,
        user_data: UserSchema
) -> None:
    user = await users_repository.delete(user_data.user_id)
    assert user
    assert user.user_id == user_data.user_id

    await users_repository.session.flush()
    users_repository.session.expire_all()

    with pytest.raises(ResultNotFound):
        await users_repository.delete(user_data.user_id)

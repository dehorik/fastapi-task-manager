from contextlib import nullcontext
from typing import ContextManager, Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from auth import TokenPayloadSchema
from exceptions import (
    UserGroupAttachError,
    UserGroupDetachError,
    GroupNotFoundError,
    ResultNotFound
)
from models import Group
from schemas import (
    GroupSchema,
    GroupSchemaCreate,
    GroupSchemaUpdate,
    GroupItemsSchema,
    GroupUsersSchema,
    GroupTasksSchema,
    UserGroupSchemaAttach
)
from services import GroupsService
from .helpers import make_fake_group


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["user_does_not_exist", "expectation"],
    [
        (True, pytest.raises(UserGroupAttachError)),
        (False, nullcontext()),
    ]
)
async def test_create_group(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        user_does_not_exist: bool,
        expectation: ContextManager[Any]
) -> None:
    fake_group_schema_create = GroupSchemaCreate(
        name="group",
        description="group"
    )

    if user_does_not_exist:
        fake_uow.groups.create = mocker.AsyncMock(
            side_effect=IntegrityError(None, None, BaseException())
        )
    else:
        fake_group_schema, fake_group_model = make_fake_group(
            **fake_group_schema_create.model_dump()
        )

        fake_uow.groups.create = mocker.AsyncMock(return_value=fake_group_model)

    groups_service = GroupsService(fake_uow)

    with expectation:
        result = await groups_service.create_group(
            fake_token_payload,
            fake_group_schema_create
        )

    fake_uow.groups.create.assert_awaited_once_with({
        "user_id": fake_token_payload.sub,
        **fake_group_schema_create.model_dump()
    })
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not user_does_not_exist:
        assert result.model_dump() == fake_group_schema.model_dump()
        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (True, False, pytest.raises(GroupNotFoundError)),
        (False, True, pytest.raises(GroupNotFoundError)),
        (False, False, nullcontext())
    ]
)
async def test_get_group(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    """
    Тест всех методов для получения информации о группе.
    Тестриует на каждом из методов поведение при отсутствии группы,
    при отсутствии прав на чтение группы, а также нормальный сценарий.

    Тестируемые методы:
    GroupsService.get_group_basic
    GroupsService.get_group_details
    GroupsService.get_group_users
    GroupsService.get_group_tasks
    """

    fake_group_id = uuid4()

    if group_not_found:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.get = mocker.AsyncMock(return_value=None)
        fake_uow.groups.get_group_details = mocker.AsyncMock(return_value=None)
        fake_uow.groups.get_group_users = mocker.AsyncMock(return_value=None)
        fake_uow.groups.get_group_tasks = mocker.AsyncMock(return_value=None)

    elif user_not_in_group:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_group_schema, fake_group_model = make_fake_group(group_id=fake_group_id)

        fake_group_items_schema = GroupItemsSchema(
            **fake_group_schema.model_dump(),
            users=[],
            tasks=[]
        )
        fake_group_users_schema = GroupUsersSchema(
            **fake_group_schema.model_dump(),
            users=[],
        )
        fake_group_tasks_schema = GroupTasksSchema(
            **fake_group_schema.model_dump(),
            tasks=[],
        )

        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.get = mocker.AsyncMock(
            return_value=fake_group_model
        )
        fake_uow.groups.get_group_details = mocker.AsyncMock(
            return_value=fake_group_items_schema
        )
        fake_uow.groups.get_group_users = mocker.AsyncMock(
            return_value=fake_group_users_schema
        )
        fake_uow.groups.get_group_tasks = mocker.AsyncMock(
            return_value=fake_group_tasks_schema
        )

    groups_service = GroupsService(fake_uow)

    with expectation:
        group_basic_result = await groups_service.get_group_basic(
            fake_token_payload,
            fake_group_id
        )
    with expectation:
        group_details_result = await groups_service.get_group_details(
            fake_token_payload,
            fake_group_id
        )
    with expectation:
        group_users_result = await groups_service.get_group_users(
            fake_token_payload,
            fake_group_id
        )
    with expectation:
        group_tasks_result = await groups_service.get_group_tasks(
            fake_token_payload,
            fake_group_id
        )

    assert fake_uow.groups.get_group_id_if_user_in_group.call_count == 4
    fake_uow.groups.get_group_id_if_user_in_group.assert_awaited_with(
        fake_token_payload.sub,
        fake_group_id
    )
    assert fake_uow.__aenter__.call_count == 4
    assert fake_uow.__aexit__.call_count == 4
    fake_uow.commit.assert_not_awaited()

    if not group_not_found and not user_not_in_group:
        assert group_basic_result.model_dump() == fake_group_schema.model_dump()
        assert group_details_result.model_dump() == fake_group_items_schema.model_dump()
        assert group_users_result.model_dump() == fake_group_users_schema.model_dump()
        assert group_tasks_result.model_dump() == fake_group_tasks_schema.model_dump()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (True, False, pytest.raises(GroupNotFoundError)),
        (False, True, pytest.raises(GroupNotFoundError)),
        (False, False, nullcontext())
    ]
)
async def test_full_update_group(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    """
    Тест поведения метода update_group при отсутствии группы, при отсутствии
    у клиента прав на обновление группы (если клиент не является участником этой группы),
    а также при полном обновлении полей группы
    """

    fake_group_id = uuid4()
    fake_group_schema_update = GroupSchemaUpdate(
        name="group",
        description="group"
    )

    if group_not_found:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.update = mocker.AsyncMock(side_effect=ResultNotFound())

    elif user_not_in_group:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_group_schema, fake_group_model = make_fake_group(
            group_id=fake_group_id,
            **fake_group_schema_update.model_dump()
        )

        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.update = mocker.AsyncMock(
            return_value=fake_group_model
        )

    groups_service = GroupsService(fake_uow)

    with expectation:
        result = await groups_service.update_group(
            fake_token_payload,
            fake_group_id,
            fake_group_schema_update
        )

    fake_uow.groups.get_group_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_group_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not group_not_found and not user_not_in_group:
        assert result.model_dump() == fake_group_schema.model_dump()
        fake_uow.groups.update.assert_awaited_once_with(
            fake_group_id,
            fake_group_schema_update.model_dump()
        )
        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["fake_group_schema_update", "fake_group_schema", "fake_group_model"],
    [
        (GroupSchemaUpdate(name="group"), *make_fake_group(name="group")),
        (GroupSchemaUpdate(), *make_fake_group())
    ]
)
async def test_partial_update_group(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        fake_group_schema_update: GroupSchemaUpdate,
        fake_group_schema: GroupSchema,
        fake_group_model: Group
) -> None:
    """
    Тест поведения метода update_group при частичном обновлении полей группы.
    Тест предполагается запускать после test_full_update_group
    """

    fake_group_id = fake_group_schema.group_id

    fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
        return_value=fake_group_id
    )
    fake_uow.groups.update = mocker.AsyncMock(
        return_value=fake_group_model
    )

    groups_service = GroupsService(fake_uow)

    result = await groups_service.update_group(
        fake_token_payload,
        fake_group_id,
        fake_group_schema_update
    )
    assert result.model_dump() == fake_group_schema.model_dump()

    fake_uow.groups.update.assert_awaited_once_with(
        fake_group_id,
        fake_group_schema_update.model_dump(exclude_none=True)
    )
    fake_uow.groups.get_group_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_group_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (True, False, pytest.raises(GroupNotFoundError)),
        (False, True, pytest.raises(GroupNotFoundError)),
        (False, False, nullcontext())
    ]
)
async def test_delete_group(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    fake_group_id = uuid4()

    if group_not_found:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.delete = mocker.AsyncMock(side_effect=ResultNotFound())

    elif user_not_in_group:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_group_schema, fake_group_model = make_fake_group(group_id=fake_group_id)

        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.delete = mocker.AsyncMock(return_value=fake_group_model)

    groups_service = GroupsService(fake_uow)

    with expectation:
        result = await groups_service.delete_group(
            fake_token_payload,
            fake_group_id
        )

    fake_uow.groups.get_group_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_group_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not group_not_found and not user_not_in_group:
        assert result.model_dump() == fake_group_schema.model_dump()

        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["group_or_user_does_not_exist", "user_not_in_group", "expectation"],
    [
        (True, False, pytest.raises(UserGroupAttachError)),
        (False, True, pytest.raises(UserGroupAttachError)),
        (False, False, nullcontext())
    ]
)
async def test_add_user_to_group(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        group_or_user_does_not_exist: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    fake_group_id = uuid4()
    fake_user_group_schema_attach = UserGroupSchemaAttach(
        user_id=uuid4()
    )

    if group_or_user_does_not_exist:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.add_user_to_group = mocker.AsyncMock(
            side_effect=IntegrityError(None, None, BaseException())
        )

    elif user_not_in_group:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.add_user_to_group = mocker.AsyncMock(return_value=None)

    groups_service = GroupsService(fake_uow)

    with expectation:
        await groups_service.add_user_to_group(
            fake_token_payload,
            fake_group_id,
            fake_user_group_schema_attach
        )

    fake_uow.groups.get_group_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_group_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not group_or_user_does_not_exist and not user_not_in_group:
        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["group_or_user_does_not_exist", "user_not_in_group", "expectation"],
    [
        (True, False, pytest.raises(UserGroupDetachError)),
        (False, True, pytest.raises(UserGroupDetachError)),
        (False, False, nullcontext())
    ]
)
async def test_remove_user_from_group(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        group_or_user_does_not_exist: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    fake_group_id = uuid4()
    fake_user_id = uuid4()

    if group_or_user_does_not_exist:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.remove_user_from_group = mocker.AsyncMock(
            side_effect=ResultNotFound()
        )

    elif user_not_in_group:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_group_id
        )
        fake_uow.groups.remove_user_from_group = mocker.AsyncMock(
            return_value=None
        )

    groups_service = GroupsService(fake_uow)

    with expectation:
        await groups_service.remove_user_from_group(
            fake_token_payload,
            fake_group_id,
            fake_user_id
        )

    fake_uow.groups.get_group_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_group_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not group_or_user_does_not_exist and not user_not_in_group:
        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()

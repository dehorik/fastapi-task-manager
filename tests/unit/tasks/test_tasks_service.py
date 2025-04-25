from contextlib import nullcontext
from typing import ContextManager, Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from auth import TokenPayloadSchema
from exceptions import NonExistentGroupError, TaskNotFoundError, ResultNotFound
from models import Task
from schemas import TaskSchemaCreate, TaskSchemaUpdate, TaskSchema
from services import TasksService
from .helpers import make_fake_task


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(NonExistentGroupError)),
        (False, True, pytest.raises(NonExistentGroupError))
    ]
)
async def test_create_task(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    fake_task_schema_create = TaskSchemaCreate(
        group_id=uuid4(),
        name="task",
        description="task",
        estimated_time=1
    )

    if group_not_found:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_schema_create.group_id
        )
        fake_uow.tasks.create = mocker.AsyncMock(
            side_effect=IntegrityError(None, None, BaseException())
        )

    elif user_not_in_group:
        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_task_schema, fake_task_model = make_fake_task(
            group_id=fake_task_schema_create.group_id,
            name=fake_task_schema_create.name,
            description=fake_task_schema_create.description,
            estimated_time=fake_task_schema_create.estimated_time
        )

        fake_uow.groups.get_group_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_schema_create.group_id
        )
        fake_uow.tasks.create = mocker.AsyncMock(return_value=fake_task_model)

    tasks_service = TasksService(fake_uow)

    with expectation:
        result = await tasks_service.create_task(
            fake_token_payload,
            fake_task_schema_create
        )

    fake_uow.groups.get_group_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub, fake_task_schema_create.group_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not group_not_found and not user_not_in_group:
        assert result.model_dump() == fake_task_schema.model_dump()
        fake_uow.tasks.create.assert_awaited_once_with(
            fake_task_schema_create.model_dump()
        )
        fake_uow.commit.assert_awaited_once()

    if group_not_found or user_not_in_group:
        fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(TaskNotFoundError)),
        (False, True, pytest.raises(TaskNotFoundError))
    ]
)
async def test_get_task(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        task_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    fake_task_id = uuid4()

    if task_not_found:
        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_id
        )
        fake_uow.tasks.get = mocker.AsyncMock(return_value=None)

    elif user_not_in_group:
        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_task_schema, fake_task_model = make_fake_task(
            task_id=fake_task_id
        )

        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_id
        )
        fake_uow.tasks.get = mocker.AsyncMock(return_value=fake_task_model)

    tasks_service = TasksService(fake_uow)

    with expectation:
        result = await tasks_service.get_task(fake_token_payload, fake_task_id)

    fake_uow.tasks.get_task_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_task_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_not_awaited()

    if not task_not_found and not user_not_in_group:
        assert result.model_dump() == fake_task_schema.model_dump()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(TaskNotFoundError)),
        (False, True, pytest.raises(TaskNotFoundError))
    ]
)
async def test_full_update_task(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        task_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    """
    Тест поведения метода update_task у сервиса задач.
    Тест проверяет поведение при отсутствии прав у пользователя на изменение задачи,
    поведение при попытке обновить несуществующую задачу, а также поведение при
    обновлении всех полей задачи
    """

    fake_task_id = uuid4()
    fake_task_schema_update = TaskSchemaUpdate(
        name="task",
        description="task",
        estimated_time=1
    )

    if task_not_found:
        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_id
        )
        fake_uow.tasks.update = mocker.AsyncMock(side_effect=ResultNotFound())

    elif user_not_in_group:
        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_task_schema, fake_task_model = make_fake_task(
            task_id=fake_task_id,
            name=fake_task_schema_update.name,
            description=fake_task_schema_update.description,
            estimated_time=fake_task_schema_update.estimated_time
        )

        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_id
        )
        fake_uow.tasks.update = mocker.AsyncMock(return_value=fake_task_model)

    tasks_service = TasksService(fake_uow)

    with expectation:
        result = await tasks_service.update_task(
            fake_token_payload,
            fake_task_id,
            fake_task_schema_update
        )

    fake_uow.tasks.get_task_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_task_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not task_not_found and not user_not_in_group:
        assert result.model_dump() == fake_task_schema.model_dump()
        fake_uow.tasks.update.assert_awaited_once_with(
            fake_task_id,
            fake_task_schema_update.model_dump()
        )
        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["fake_task_schema_update", "fake_task_schema", "fake_task_model"],
    [
        (TaskSchemaUpdate(name="task"), *make_fake_task(name="task")),
        (TaskSchemaUpdate(), *make_fake_task()),
    ]
)
async def test_partial_update_task(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        fake_task_schema_update: TaskSchemaUpdate,
        fake_task_schema: TaskSchema,
        fake_task_model: Task
) -> None:
    """
    Тест поведения метода update_task у сервиса задач при
    частичном обнолвнии задачи. Тест предполагает, что задача
    существует и что у вызывающего клиента есть право на совершение
    этого действия. Предполагается вызов этого теста после test_full_update_task
    """

    fake_task_id = fake_task_schema.task_id

    fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
        return_value=fake_task_id
    )
    fake_uow.tasks.update = mocker.AsyncMock(return_value=fake_task_model)

    tasks_service = TasksService(fake_uow)

    result = await tasks_service.update_task(
        fake_token_payload,
        fake_task_id,
        fake_task_schema_update
    )
    assert result.model_dump() == fake_task_schema.model_dump()

    fake_uow.tasks.update.assert_awaited_once_with(
        fake_task_id,
        fake_task_schema_update.model_dump(exclude_none=True)
    )
    fake_uow.tasks.get_task_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_task_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()
    fake_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.parametrize(
    ["task_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(TaskNotFoundError)),
        (False, True, pytest.raises(TaskNotFoundError))
    ]
)
async def test_delete_task(
        mocker: MockerFixture,
        fake_uow: Mock,
        fake_token_payload: TokenPayloadSchema,
        task_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    fake_task_id = uuid4()

    if task_not_found:
        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_id
        )
        fake_uow.tasks.delete = mocker.AsyncMock(side_effect=ResultNotFound())

    elif user_not_in_group:
        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=None
        )

    else:
        fake_task_schema, fake_task_model = make_fake_task(task_id=fake_task_id)

        fake_uow.tasks.get_task_id_if_user_in_group = mocker.AsyncMock(
            return_value=fake_task_id
        )
        fake_uow.tasks.delete = mocker.AsyncMock(return_value=fake_task_model)

    tasks_service = TasksService(fake_uow)

    with expectation:
        result = await tasks_service.delete_task(fake_token_payload, fake_task_id)

    fake_uow.tasks.get_task_id_if_user_in_group.assert_awaited_once_with(
        fake_token_payload.sub,
        fake_task_id
    )
    fake_uow.__aenter__.assert_awaited_once()
    fake_uow.__aexit__.assert_awaited_once()

    if not task_not_found and not user_not_in_group:
        assert result.model_dump() == fake_task_schema.model_dump()
        fake_uow.commit.assert_awaited_once()
    else:
        fake_uow.commit.assert_not_awaited()

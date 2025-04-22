from contextlib import nullcontext
from random import randint, choice
from typing import Callable, Awaitable, ContextManager, Any
from uuid import uuid4, UUID

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import (
    GroupNotFoundError,
    UserGroupAttachError,
    UserGroupDetachError
)
from models import Group
from schemas import (
    GroupSchema,
    GroupSchemaCreate,
    GroupSchemaUpdate,
    GroupPreviewSchema,
    GroupPreviewListSchema,
    GroupItemsSchema,
    GroupUsersSchema,
    GroupTasksSchema,
    UserSchema,
    UserPreviewSchema,
    TaskSchema,
    TaskPreviewSchema,
    UserGroupSchemaAttach
)
from services import GroupsService
from .helpers import generate_group_name, generate_group_description
from ..helpers import get_fake_token_payload


@pytest.mark.asyncio
@pytest.mark.integration
async def test_check_user_access_to_group(
        groups_service: GroupsService,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable]
) -> None:
    members_data = [
        await users_factory()
        for _ in range(randint(2, 4))
    ]
    users_data = [
        await users_factory()
        for _ in range(randint(2, 4))
    ]

    group_data = await groups_factory(members_data[0].user_id)

    for member_data in members_data[1:]:
        await users_groups_relations_factory(
            group_data.group_id,
            member_data.user_id
        )

    async with groups_service.uow as uow:
        for member_data in members_data:
            assert await groups_service._check_user_access_to_group(
                uow,
                member_data.user_id,
                group_data.group_id
            )

        for user_data in users_data:
            assert not await groups_service._check_user_access_to_group(
                uow,
                user_data.user_id,
                group_data.group_id
            )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found", "expectation"],
    [
        (False, nullcontext()),
        (True, pytest.raises(UserGroupAttachError))
    ]
)
async def test_create_group(
        session: AsyncSession,
        groups_service: GroupsService,
        users_factory: Callable[[], Awaitable[UserSchema]],
        user_not_found: bool,
        expectation: ContextManager[Any]
) -> None:
    user_data = await users_factory()

    if user_not_found:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    group_schema_create = GroupSchemaCreate(
        name=generate_group_name(),
        description=generate_group_description()
    )

    with expectation:
        group = await groups_service.create_group(payload, group_schema_create)

    if not user_not_found:
        await session.execute(
            delete(Group)
            .where(Group.group_id == group.group_id)
        )
        await session.commit()

        assert group.name == group_schema_create.name
        assert group.description == group_schema_create.description


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(GroupNotFoundError)),
        (False, True, pytest.raises(GroupNotFoundError))
    ]
)
async def test_get_group(
        groups_service: GroupsService,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable],
        tasks_factory: Callable[[UUID], Awaitable[TaskSchema]],
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    """
    Проверяет доступ и корректность данных всех методов для получения информации о группе.

    Тестируемые методы:
    GroupsService.get_group_basic
    GroupsService.get_group_details
    GroupsService.get_group_users
    GroupsService.get_group_tasks
    """

    users_data = [await users_factory() for _ in range(randint(2, 4))]
    users_preview_data = [
        UserPreviewSchema(user_id=user_data.user_id, username=user_data.username)
        for user_data in users_data
    ]
    users_preview_data.sort(key=lambda data: data.user_id)

    group_data = await groups_factory(users_preview_data[0].user_id)

    for user_preview_data in users_preview_data[1:]:
        await users_groups_relations_factory(
            group_data.group_id,
            user_preview_data.user_id
        )

    tasks_data = [
        await tasks_factory(group_data.group_id)
        for _ in range(randint(2, 4))
    ]
    tasks_preview_data = [
        TaskPreviewSchema(task_id=task_data.task_id, name=task_data.name)
        for task_data in tasks_data
    ]
    tasks_preview_data.sort(key=lambda data: data.task_id)

    group_items_data = GroupItemsSchema(
        **group_data.model_dump(),
        users=users_preview_data,
        tasks=tasks_preview_data
    )
    group_users_data = GroupUsersSchema(
        **group_data.model_dump(),
        users=users_preview_data
    )
    group_tasks_data = GroupTasksSchema(
        **group_data.model_dump(),
        tasks=tasks_preview_data
    )

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(choice(users_preview_data).user_id)

    group_id = uuid4() if group_not_found else group_data.group_id

    with expectation:
        group_basic = await groups_service.get_group_basic(payload, group_id)

    with expectation:
        group_items = await groups_service.get_group_details(payload, group_id)

    with expectation:
        group_users = await groups_service.get_group_users(payload, group_id)

    with expectation:
        group_tasks = await groups_service.get_group_tasks(payload, group_id)

    if not group_not_found and not user_not_in_group:
        group_items.users.sort(key=lambda data: data.user_id)
        group_items.tasks.sort(key=lambda data: data.task_id)
        group_users.users.sort(key=lambda data: data.user_id)
        group_tasks.tasks.sort(key=lambda data: data.task_id)

        assert group_basic.model_dump() == group_data.model_dump()
        assert group_items.model_dump() == group_items_data.model_dump()
        assert group_users.model_dump() == group_users_data.model_dump()
        assert group_tasks.model_dump() == group_tasks_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["user_not_found", "expectation"],
    [
        (False, nullcontext()),
        (True, nullcontext())
    ]
)
async def test_get_user_groups_list(
        groups_service: GroupsService,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        user_not_found: bool,
        expectation: ContextManager[Any]
) -> None:
    user_data = await users_factory()

    groups_data = [
        await groups_factory(user_data.user_id)
        for _ in range(randint(2, 4))
    ]
    groups_preview_data = [
        GroupPreviewSchema(group_id=group_data.group_id, name=group_data.name)
        for group_data in groups_data
    ]
    groups_preview_data.sort(key=lambda data: data.group_id)
    group_preview_list_data = GroupPreviewListSchema(groups=groups_preview_data)

    payload = get_fake_token_payload(uuid4() if user_not_found else user_data.user_id)

    with expectation:
        group_preview_list = await groups_service.get_user_groups_list(payload)

    if not user_not_found:
        group_preview_list.groups.sort(key=lambda data: data.group_id)
        assert group_preview_list.model_dump() == group_preview_list_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(GroupNotFoundError)),
        (False, True, pytest.raises(GroupNotFoundError))
    ]
)
async def test_update_group(
        groups_service: GroupsService,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    """
    Тест метода GroupsService.update_group
    Проверяет и полное обновление полей группы, и частичное
    """

    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    group_schema_update = GroupSchemaUpdate(
        name=generate_group_name(),
        description=generate_group_description()
    )
    group_data.name = group_schema_update.name
    group_data.description = group_schema_update.description

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    group_id = uuid4() if group_not_found else group_data.group_id

    with expectation:
        group = await groups_service.update_group(
            payload,
            group_id,
            group_schema_update
        )

    if not group_not_found and not user_not_in_group:
        assert group.model_dump() == group_data.model_dump()

        group_schema_update = GroupSchemaUpdate(name=generate_group_name())
        group_data.name = group_schema_update.name

        group = await groups_service.update_group(
            payload,
            group_id,
            group_schema_update
        )

        assert group.model_dump() == group_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "expectation"],
    [
        (False, False, nullcontext()),
        (True, False, pytest.raises(GroupNotFoundError)),
        (False, True, pytest.raises(GroupNotFoundError))
    ]
)
async def test_delete_group(
        groups_service: GroupsService,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        group_not_found: bool,
        user_not_in_group: bool,
        expectation: ContextManager[Any]
) -> None:
    user_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    group_id = uuid4() if group_not_found else group_data.group_id

    with expectation:
        group = await groups_service.delete_group(payload, group_id)

    if not group_not_found and not user_not_in_group:
        assert group.model_dump() == group_data.model_dump()

        with pytest.raises(GroupNotFoundError):
            await groups_service.delete_group(payload, group_id)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    [
        "group_not_found",
        "user_not_in_group",
        "user_is_already_member",
        "user_not_found",
        "expectation"
    ],
    [
        (False, False, False, False, nullcontext()),
        (True, False, False, False, pytest.raises(UserGroupAttachError)),
        (False, True, False, False, pytest.raises(UserGroupAttachError)),
        (False, False, True, False, pytest.raises(UserGroupAttachError)),
        (False, False, False, True, pytest.raises(UserGroupAttachError))
    ]
)
async def test_add_user_to_group(
        groups_service: GroupsService,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable],
        group_not_found: bool,
        user_not_in_group: bool,
        user_is_already_member: bool,
        user_not_found: bool,
        expectation: ContextManager[Any]
) -> None:
    """
    Тест метода GroupsService.add_user_to_group

    Проверяет:
    1) нормальное поведение (все флаги False)
    2) попытку получить доступ к несуществующей группе
    (флаг group_not_found)
    3) попытку получения доступа к группе клиентом, котрый
    не является участником этой группы (флаг user_not_in_group)
    4) попытку добавить в группу пользователя, котрый уже в ней
    находится (флаг user_is_already_member)
    5) попытку добавить в группу несуществующего пользователя
    (флаг user_not_found)
    """

    user_data = await users_factory()
    new_member_data = await users_factory()
    group_data = await groups_factory(user_data.user_id)

    group_id = uuid4() if group_not_found else group_data.group_id

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    if user_not_found:
        attach_schema = UserGroupSchemaAttach(user_id=uuid4())
    else:
        attach_schema = UserGroupSchemaAttach(user_id=new_member_data.user_id)

    if user_is_already_member:
        await users_groups_relations_factory(
            group_data.group_id,
            new_member_data.user_id
        )

    with expectation:
        await groups_service.add_user_to_group(payload, group_id, attach_schema)

    if not any([group_not_found, user_not_in_group, user_is_already_member, user_not_found]):
        group = await groups_service.get_group_basic(
            get_fake_token_payload(new_member_data.user_id),
            group_data.group_id
        )
        assert group.model_dump() == group_data.model_dump()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ["group_not_found", "user_not_in_group", "member_not_found", "expectation"],
    [
        (False, False, False, nullcontext()),
        (True, False, False, pytest.raises(UserGroupDetachError)),
        (False, True, False, pytest.raises(UserGroupDetachError)),
        (False, False, True, pytest.raises(UserGroupDetachError))
    ]
)
async def test_remove_user_from_group(
        groups_service: GroupsService,
        groups_factory: Callable[[UUID], Awaitable[GroupSchema]],
        users_factory: Callable[[], Awaitable[UserSchema]],
        users_groups_relations_factory: Callable[[UUID, UUID], Awaitable],
        group_not_found: bool,
        user_not_in_group: bool,
        member_not_found: bool,
        expectation: ContextManager[Any]
) -> None:
    """
    Тест метода GroupsService.remove_user_from_group

    Проверяет:
    1) нормальное поведение (все флаги False)
    2) поведение при попытке удалить участника из несуществующей группы
    (флаг group_not_found)
    3) поведение при попытке клиента полчить доступ к группе, участником
    котрой он не является (флаг user_not_in_group)
    4) поведение при попытке удалить из группы несуществующего участника
    (флаг member_not_found)
    """

    user_data = await users_factory()
    member_data = await users_factory()

    group_data = await groups_factory(user_data.user_id)
    await users_groups_relations_factory(group_data.group_id, member_data.user_id)

    group_id = uuid4() if group_not_found else group_data.group_id

    if user_not_in_group:
        payload = get_fake_token_payload(uuid4())
    else:
        payload = get_fake_token_payload(user_data.user_id)

    member_id = uuid4() if member_not_found else member_data.user_id

    with expectation:
        await groups_service.remove_user_from_group(payload, group_id, member_id)

    if not any([group_not_found, user_not_in_group, member_not_found]):
        with pytest.raises(GroupNotFoundError):
            await groups_service.get_group_basic(
                get_fake_token_payload(member_data.user_id),
                group_data.group_id
            )

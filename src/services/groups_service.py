from uuid import UUID

from sqlalchemy.exc import IntegrityError

from exceptions import (
    GroupNotFoundError,
    UserGroupAttachError,
    UserGroupDetachError,
    ResultNotFound
)
from interfaces import AbstractUnitOfWork
from schemas import (
    GroupSchema,
    GroupItemsSchema,
    GroupSchemaCreate,
    GroupSchemaUpdate,
    UserGroupSchemaAttach,
    GroupPreviewListSchema,
    GroupPreviewSchema, GroupUsersSchema, GroupTasksSchema
)


class GroupsService:
    """Сервис для работы с группами задач"""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_group(self, data: GroupSchemaCreate) -> GroupSchema:
        try:
            async with self.uow as uow:
                group = await uow.groups.create(data.model_dump())
                await uow.commit()

            return GroupSchema.model_validate(group, from_attributes=True)
        except IntegrityError:
            raise UserGroupAttachError("user does not exist")

    async def get_group_basic(self, group_id: UUID) -> GroupSchema:
        """Получение всей информации о группе"""

        async with self.uow as uow:
            group = await uow.groups.get(group_id)

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupSchema.model_validate(group, from_attributes=True)

    async def get_group_details(self, group_id: UUID) -> GroupItemsSchema:
        """
        Получение всей информации о группе,
        включая данные о пользователях в этой группе и списке ее задач
        """

        async with self.uow as uow:
            group = await uow.groups.get_group_details(group_id)

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupItemsSchema.model_validate(group, from_attributes=True)

    async def get_group_users(self, group_id: UUID) -> GroupUsersSchema:
        """Получение всей информации о группе, включая список ее пользователей"""

        async with self.uow as uow:
            group = await uow.groups.get_group_users(group_id)

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupUsersSchema.model_validate(group, from_attributes=True)

    async def get_group_tasks(self, group_id: UUID) -> GroupTasksSchema:
        """Получение всей информации о группе, включая связанные с ней задачи"""

        async with self.uow as uow:
            group = await uow.groups.get_group_tasks(group_id)

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupTasksSchema.model_validate(group, from_attributes=True)

    async def get_user_groups_list(self, user_id: UUID) -> GroupPreviewListSchema:
        """
        Получение списка из групп пользователя,
        содержащего идентифицирующие данные о группе
        """

        async with self.uow as uow:
            groups = await uow.groups.get_user_groups_list(user_id)

        groups = [
            GroupPreviewSchema.model_validate(group, from_attributes=True)
            for group in groups
        ]
        return GroupPreviewListSchema(groups=groups)

    async def update_group(self, group_id: UUID, data: GroupSchemaUpdate) -> GroupSchema:
        try:
            async with self.uow as uow:
                group = await uow.groups.update(
                    group_id,
                    {
                        key: value
                        for key, value in data.model_dump().items()
                        if value is not None
                    }
                )
                await uow.commit()

            return GroupSchema.model_validate(group, from_attributes=True)
        except ResultNotFound:
            raise GroupNotFoundError("group not found")

    async def delete_group(self, group_id: UUID) -> GroupSchema:
        try:
            async with self.uow as uow:
                group = await uow.groups.delete(group_id)
                await uow.commit()

            return GroupSchema.model_validate(group, from_attributes=True)
        except ResultNotFound:
            raise GroupNotFoundError("group not found")

    async def add_user_to_group(self, group_id: UUID, data: UserGroupSchemaAttach) -> None:
        try:
            async with self.uow as uow:
                await uow.groups.add_user_to_group(group_id, data.user_id)
                await uow.commit()
        except IntegrityError:
            raise UserGroupAttachError("cannot add user to group")

    async def remove_user_from_group(self, group_id: UUID, user_id: UUID) -> None:
        try:
            async with self.uow as uow:
                await uow.groups.remove_user_from_group(group_id, user_id)
                await uow.commit()
        except ResultNotFound:
            raise UserGroupDetachError("cannot remove user from group")

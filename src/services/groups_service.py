from uuid import UUID

from sqlalchemy.exc import IntegrityError

from auth import TokenPayloadSchema
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
    GroupPreviewSchema,
    GroupUsersSchema,
    GroupTasksSchema
)


class GroupsService:
    """Сервис для работы с группами задач"""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @staticmethod
    async def _check_user_access_to_group(
            uow: AbstractUnitOfWork,
            user_id: UUID,
            group_id: UUID
    ) -> bool:
        """
        Проверка присутствия пользователя с user_id в группе с group_id

        :param uow: объект unit of work с открытой сессией
        (объект нужно открыть через асинхронный контекстный менеджер)
        :param user_id: user_id проверяемого пользователя
        :param group_id: group_id группы, к которой пользователь должен относиться
        :return: True/False в зависимости от результата проверки
        """

        return bool(await uow.groups.get_group_id_if_user_in_group(user_id, group_id))

    async def create_group(
            self,
            payload: TokenPayloadSchema,
            data: GroupSchemaCreate
    ) -> GroupSchema:
        try:
            async with self.uow as uow:
                group = await uow.groups.create({
                    "user_id": payload.sub,
                    **data.model_dump()
                })
                await uow.commit()

            return GroupSchema.model_validate(group, from_attributes=True)
        except IntegrityError:
            raise UserGroupAttachError("user does not exist")

    async def get_group_basic(
            self,
            payload: TokenPayloadSchema,
            group_id: UUID
    ) -> GroupSchema:
        """Получение всей информации о группе"""

        async with self.uow as uow:
            if await self._check_user_access_to_group(uow, payload.sub, group_id):
                group = await uow.groups.get(group_id)
            else:
                raise GroupNotFoundError("group not found")

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupSchema.model_validate(group, from_attributes=True)

    async def get_group_details(
            self,
            paylaod: TokenPayloadSchema,
            group_id: UUID
    ) -> GroupItemsSchema:
        """
        Получение всей информации о группе,
        включая данные о пользователях в этой группе и списке ее задач
        """

        async with self.uow as uow:
            if await self._check_user_access_to_group(uow, paylaod.sub, group_id):
                group = await uow.groups.get_group_details(group_id)
            else:
                raise GroupNotFoundError("group not found")

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupItemsSchema.model_validate(group, from_attributes=True)

    async def get_group_users(
            self,
            payload: TokenPayloadSchema,
            group_id: UUID) -> GroupUsersSchema:
        """Получение всей информации о группе, включая список ее пользователей"""

        async with self.uow as uow:
            if await self._check_user_access_to_group(uow, payload.sub, group_id):
                group = await uow.groups.get_group_users(group_id)
            else:
                raise GroupNotFoundError("group not found")

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupUsersSchema.model_validate(group, from_attributes=True)

    async def get_group_tasks(
            self,
            payload: TokenPayloadSchema,
            group_id: UUID
    ) -> GroupTasksSchema:
        """Получение всей информации о группе, включая связанные с ней задачи"""

        async with self.uow as uow:
            if await self._check_user_access_to_group(uow, payload.sub, group_id):
                group = await uow.groups.get_group_tasks(group_id)
            else:
                raise GroupNotFoundError("group not found")

        if group is None:
            raise GroupNotFoundError("group not found")

        return GroupTasksSchema.model_validate(group, from_attributes=True)

    async def get_user_groups_list(
            self,
            paylaod: TokenPayloadSchema
    ) -> GroupPreviewListSchema:
        """
        Получение списка из групп пользователя,
        содержащего идентифицирующие данные о группе
        """

        async with self.uow as uow:
            groups = await uow.groups.get_user_groups_list(paylaod.sub)

        groups = [
            GroupPreviewSchema.model_validate(group, from_attributes=True)
            for group in groups
        ]
        return GroupPreviewListSchema(groups=groups)

    async def update_group(
            self,
            paylaod: TokenPayloadSchema,
            group_id: UUID,
            data: GroupSchemaUpdate
    ) -> GroupSchema:
        try:
            async with self.uow as uow:
                if await self._check_user_access_to_group(uow, paylaod.sub, group_id):
                    group = await uow.groups.update(
                        group_id,
                        data.model_dump(exclude_none=True)
                    )
                    await uow.commit()
                else:
                    raise GroupNotFoundError("group not found")

            return GroupSchema.model_validate(group, from_attributes=True)
        except ResultNotFound:
            raise GroupNotFoundError("group not found")

    async def delete_group(
            self,
            payload: TokenPayloadSchema,
            group_id: UUID
    ) -> GroupSchema:
        try:
            async with self.uow as uow:
                if await self._check_user_access_to_group(uow, payload.sub, group_id):
                    group = await uow.groups.delete(group_id)
                    await uow.commit()
                else:
                    raise GroupNotFoundError("group not found")

            return GroupSchema.model_validate(group, from_attributes=True)
        except ResultNotFound:
            raise GroupNotFoundError("group not found")

    async def add_user_to_group(
            self,
            payload: TokenPayloadSchema,
            group_id: UUID,
            data: UserGroupSchemaAttach
    ) -> None:
        try:
            async with self.uow as uow:
                if await self._check_user_access_to_group(uow, payload.sub, group_id):
                    await uow.groups.add_user_to_group(group_id, data.user_id)
                    await uow.commit()
                else:
                    raise UserGroupAttachError("cannot add user to group")
        except IntegrityError:
            raise UserGroupAttachError("cannot add user to group")

    async def remove_user_from_group(
            self,
            payload: TokenPayloadSchema,
            group_id: UUID,
            user_id: UUID
    ) -> None:
        try:
            async with self.uow as uow:
                if await self._check_user_access_to_group(uow, payload.sub, group_id):
                    await uow.groups.remove_user_from_group(group_id, user_id)
                    await uow.commit()
                else:
                    raise UserGroupDetachError("cannot remove user from group")
        except ResultNotFound:
            raise UserGroupDetachError("cannot remove user from group")

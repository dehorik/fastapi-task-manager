from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound

from exceptions import (
    GroupNotFoundError,
    NonExistentUserError,
    UserGroupAttachError,
    UserGroupDetachError
)
from interfaces import AbstractUnitOfWork
from schemas import (
    GroupSchema,
    GroupItemsSchema,
    GroupSchemaCreate,
    GroupSchemaUpdate,
    UserGroupSchemaAttach
)


class GroupsService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_group(self, data: GroupSchemaCreate) -> GroupSchema:
        try:
            async with self.uow as uow:
                group = await uow.groups.create(data.model_dump())
                await uow.commit()

            group = GroupSchema.model_validate(group, from_attributes=True)
            return group
        except IntegrityError:
            raise NonExistentUserError("User with the given user_id does not exist")

    async def get_group(self, group_id: UUID) -> GroupSchema:
        async with self.uow as uow:
            group = await uow.groups.get(group_id)

        if group is None:
            raise GroupNotFoundError(f"group with group_id={group_id} not found")

        group = GroupSchema.model_validate(group, from_attributes=True)
        return group

    async def get_full_group_data(self, group_id: UUID) -> GroupItemsSchema:
        async with self.uow as uow:
            group = await uow.groups.get_full_data(group_id)

        if group is None:
            raise GroupNotFoundError(f"group with group_id={group_id} not found")

        group = GroupItemsSchema.model_validate(group, from_attributes=True)
        return group

    async def update_group(self, group_id: UUID, data: GroupSchemaUpdate) -> GroupSchema:
        try:
            async with self.uow as uow:
                group = await uow.groups.update(group_id, data.model_dump())
                await uow.commit()

            return group
        except NoResultFound:
            raise GroupNotFoundError(f"group with group_id={group_id} not found")

    async def delete_group(self, group_id: UUID) -> GroupSchema:
        try:
            async with self.uow as uow:
                group = await uow.groups.delete(group_id)
                await uow.commit()

            return group
        except NoResultFound:
            raise GroupNotFoundError(f"group with group_id={group_id} not found")

    async def add_user_to_group(self, group_id: UUID, data: UserGroupSchemaAttach) -> None:
        try:
            async with self.uow as uow:
                await uow.groups.add_user(group_id, data.user_id)
                await uow.commit()
        except IntegrityError:
            raise UserGroupAttachError("cannot add user to group")

    async def remove_user_from_group(self, group_id: UUID, user_id: UUID) -> None:
        try:
            async with self.uow as uow:
                await uow.groups.remove_user(group_id, user_id)
                await uow.commit()
        except NoResultFound:
            raise UserGroupDetachError("cannot remove user from group")

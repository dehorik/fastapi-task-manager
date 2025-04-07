from uuid import uuid4, UUID

from sqlalchemy.exc import NoResultFound

from exceptions import UserNotFoundError
from interfaces import AbstractUnitOfWork
from schemas import UserSchema, UserSchemaCreate, UserSchemaUpdate


class UsersService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_user(self, user: UserSchemaCreate) -> UserSchema:
        async with self.uow as uow:
            user = await uow.users.add({"user_id": uuid4(), **user.model_dump()})
            await uow.commit()

        user = UserSchema.model_validate(user, from_attributes=True)
        return user

    async def get_user(self, user_id: UUID) -> UserSchema:
        async with self.uow as uow:
            user = await uow.users.get(user_id)

        if user is None:
            raise UserNotFoundError(f"user with user_id={user_id} not found")

        user = UserSchema.model_validate(user, from_attributes=True)
        return user

    async def update_user(self, user_id: UUID, data: UserSchemaUpdate) -> UserSchema:
        try:
            async with self.uow as uow:
                user = await uow.users.update(user_id, data.model_dump())
                await uow.commit()

            user = UserSchema.model_validate(user, from_attributes=True)
            return user
        except NoResultFound:
            raise UserNotFoundError(f"user with user_id={user_id} not found")

    async def delete_user(self, user_id: UUID) -> UserSchema:
        try:
            async with self.uow as uow:
                user = await uow.users.remove(user_id)
                await uow.commit()

            user = UserSchema.model_validate(user, from_attributes=True)
            return user
        except NoResultFound:
            raise UserNotFoundError(f"user with user_id={user_id} not found")

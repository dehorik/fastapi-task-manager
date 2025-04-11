from uuid import uuid4, UUID

from sqlalchemy.exc import IntegrityError

from exceptions import UserNotFoundError, UsernameTakenError, ResultNotFound
from interfaces import AbstractUnitOfWork
from schemas import UserSchema, UserSchemaCreate, UserSchemaUpdate


class UsersService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_user(self, data: UserSchemaCreate) -> UserSchema:
        try:
            async with self.uow as uow:
                user = await uow.users.create({"user_id": uuid4(), **data.model_dump()})
                await uow.commit()

            return UserSchema.model_validate(user, from_attributes=True)
        except IntegrityError:
            raise UsernameTakenError("username is already taken")

    async def get_user(self, user_id: UUID) -> UserSchema:
        async with self.uow as uow:
            user = await uow.users.get(user_id)

        if user is None:
            raise UserNotFoundError("user not found")

        return UserSchema.model_validate(user, from_attributes=True)

    async def update_user(self, user_id: UUID, data: UserSchemaUpdate) -> UserSchema:
        try:
            async with self.uow as uow:
                user = await uow.users.update(
                    user_id,
                    {
                        key: value
                        for key, value in data.model_dump().items()
                        if value is not None
                    }
                )
                await uow.commit()

            return UserSchema.model_validate(user, from_attributes=True)
        except ResultNotFound:
            raise UserNotFoundError("user not found")
        except IntegrityError:
            raise UsernameTakenError("username is already taken")

    async def delete_user(self, user_id: UUID) -> UserSchema:
        try:
            async with self.uow as uow:
                user = await uow.users.delete(user_id)
                await uow.commit()

            return UserSchema.model_validate(user, from_attributes=True)
        except ResultNotFound:
            raise UserNotFoundError("user not found")

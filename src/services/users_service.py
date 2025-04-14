from sqlalchemy.exc import IntegrityError

from auth import TokenPayloadSchema, get_password_hash
from exceptions import UserNotFoundError, UsernameTakenError, ResultNotFound
from interfaces import AbstractUnitOfWork
from schemas import UserSchema, UserSchemaUpdate


class UsersService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get_user(self, payload: TokenPayloadSchema) -> UserSchema:
        async with self.uow as uow:
            user = await uow.users.get(payload.sub)

        if user is None:
            raise UserNotFoundError("user not found")

        return UserSchema.model_validate(user, from_attributes=True)

    async def update_user(
            self,
            payload: TokenPayloadSchema,
            data: UserSchemaUpdate
    ) -> UserSchema:
        try:
            fields_for_update = {
                key: value
                for key, value in data.model_dump(exclude={"password"}, exclude_none=True).items()
            }
            if data.password:
                fields_for_update["hashed_password"] = get_password_hash(data.password)

            async with self.uow as uow:
                user = await uow.users.update(payload.sub, fields_for_update)
                await uow.commit()

            return UserSchema.model_validate(user, from_attributes=True)
        except ResultNotFound:
            raise UserNotFoundError("user not found")
        except IntegrityError:
            raise UsernameTakenError("username is already taken")

    async def delete_user(self, paylaod: TokenPayloadSchema) -> UserSchema:
        try:
            async with self.uow as uow:
                user = await uow.users.delete(paylaod.sub)
                await uow.commit()

            return UserSchema.model_validate(user, from_attributes=True)
        except ResultNotFound:
            raise UserNotFoundError("user not found")

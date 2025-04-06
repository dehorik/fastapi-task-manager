from uuid import uuid4

from interfaces import AbstractUnitOfWork
from schemas import UserSchemaCreate, UserSchema


class UsersService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_user(self, user: UserSchemaCreate) -> UserSchema:
        async with self.uow as uow:
            user = await uow.users.add({"user_id": uuid4(), **user.model_dump()})
            await uow.commit()

        user = UserSchema.model_validate(user, from_attributes=True)
        return user

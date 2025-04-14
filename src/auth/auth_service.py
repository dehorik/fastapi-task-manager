from sqlalchemy.exc import IntegrityError

from interfaces import AbstractUnitOfWork
from .exceptions import UsernameTakenError, InvalidCredentialsError
from .hashing import get_password_hash, verify_password
from .schemas import CredentialsSchema, TokenSchema, TokenPayloadSchema
from .tokens import encode_token


class AuthService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def register(self, credentials: CredentialsSchema) -> TokenSchema:
        try:
            async with self.uow as uow:
                user = await uow.users.create({
                    "username": credentials.username,
                    "hashed_password": get_password_hash(credentials.password)
                })
                await uow.commit()

            return TokenSchema(token=encode_token({"sub": str(user.user_id)}))
        except IntegrityError:
            raise UsernameTakenError("username is already taken")

    async def login(self, credentials: CredentialsSchema) -> TokenSchema:
        async with self.uow as uow:
            user = await uow.users.get_user_by_username(credentials.username)

        if user is None:
            raise InvalidCredentialsError("invalid credentials")
        elif not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsError("invalid credentials")

        return TokenSchema(token=encode_token({"sub": str(user.user_id)}))

    async def refresh(self, payload: TokenPayloadSchema) -> TokenSchema:
        return TokenSchema(token=encode_token({"sub": str(payload.sub)}))

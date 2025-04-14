from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CredentialsSchema(BaseModel):
    """Данные для входа в аккаунт или регистрации"""

    username: str = Field(min_length=4, max_length=18)
    password: str = Field(min_length=8, max_length=18)


class TokenPayloadSchema(BaseModel):
    """payload токена"""

    sub: UUID
    iat: datetime
    exp: datetime


class TokenSchema(BaseModel):
    """jwt"""

    token: str

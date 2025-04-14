from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core import database_helper
from infrastructure import SQLAlchemyUnitOfWork
from interfaces import AbstractUnitOfWork
from .auth_service import AuthService
from .schemas import TokenPayloadSchema
from .tokens import decode_token


http_bearer = HTTPBearer()


def verify_token(
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]
) -> TokenPayloadSchema:
    try:
        return TokenPayloadSchema(**decode_token(token.credentials))
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )


def get_unit_of_work() -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork(database_helper.session_factory)


def get_auth_service(
        uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)]
) -> AuthService:
    return AuthService(uow)

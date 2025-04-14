from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from .auth_service import AuthService
from .dependencies import verify_token, get_auth_service
from .exceptions import UsernameTakenError, InvalidCredentialsError
from .schemas import CredentialsSchema, TokenPayloadSchema, TokenSchema


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED
)
async def register(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        credentials: CredentialsSchema
):
    try:
        return await auth_service.register(credentials)
    except UsernameTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username is already taken"
        )


@router.post(
    "/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK
)
async def login(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        credentials: CredentialsSchema
):
    try:
        return await auth_service.login(credentials)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials"
        )


@router.post(
    "/refresh",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK
)
async def refresh(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    return await auth_service.refresh(payload)


@router.post(
    "/logout",
    dependencies=[Depends(verify_token)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout():
    return None

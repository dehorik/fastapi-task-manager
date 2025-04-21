from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from auth import TokenPayloadSchema, verify_token
from exceptions import UserNotFoundError, UsernameTakenError
from schemas import UserSchema, UserSchemaUpdate, GroupPreviewListSchema
from services import UsersService, GroupsService
from .dependencies import get_users_service, get_groups_service


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        users_servidce: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        return await users_servidce.get_user(payload)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )


@router.patch(
    "/me",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK
)
async def update_user(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        users_service: Annotated[UsersService, Depends(get_users_service)],
        data: UserSchemaUpdate
):
    try:
        return await users_service.update_user(payload, data)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    except UsernameTakenError:
        raise HTTPException(
            detail="username is already taken",
            status_code=status.HTTP_409_CONFLICT
        )


@router.delete(
    "/me",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK
)
async def delete_user(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        return await users_service.delete_user(payload)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )


@router.get(
    "/me/groups",
    response_model=GroupPreviewListSchema,
    status_code=status.HTTP_200_OK
)
async def get_user_groups_list(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    return await groups_service.get_user_groups_list(payload)

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from exceptions import UserNotFoundError, UsernameTakenError
from schemas import UserSchema, UserSchemaCreate, UserSchemaUpdate, GroupPreviewListSchema
from services import UsersService, GroupsService
from .dependencies import get_users_service, get_groups_service


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
        data: UserSchemaCreate,
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        return await users_service.create_user(data)
    except UsernameTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username is already taken"
        )


@router.get("/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(
        user_id: UUID,
        users_servidce: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        return await users_servidce.get_user(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )


@router.put("/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def update_user(
        user_id: UUID,
        data: UserSchemaUpdate,
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        return await users_service.update_user(user_id, data)
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


@router.delete("/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def delete_user(
        user_id: UUID,
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        return await users_service.delete_user(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )


@router.get("/{user_id}/groups", response_model=GroupPreviewListSchema, status_code=status.HTTP_200_OK)
async def get_user_groups_list(
        user_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    return await groups_service.get_user_groups_list(user_id)

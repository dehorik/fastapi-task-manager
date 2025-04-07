from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from exceptions import UserNotFoundError
from schemas import UserSchema, UserSchemaCreate, UserSchemaUpdate
from services import UsersService
from .dependencies import get_users_service


router = APIRouter(prefix="/users")


@router.post(path="", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
        user: UserSchemaCreate,
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        user = await users_service.create_user(user)
        return user
    except IntegrityError:
        raise HTTPException(
            detail="username is already taken",
            status_code=status.HTTP_409_CONFLICT
        )


@router.get(path="/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(
        user_id: UUID,
        users_servidce: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        user = await users_servidce.get_user(user_id)
        return user
    except UserNotFoundError:
        raise HTTPException(
            detail="user not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.put(path="/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def update_user(
        user_id: UUID,
        user: UserSchemaUpdate,
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        user = await users_service.update_user(user_id, user)
        return user
    except UserNotFoundError:
        raise HTTPException(
            detail="user not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except IntegrityError:
        raise HTTPException(
            detail="username is already taken",
            status_code=status.HTTP_409_CONFLICT
        )


@router.delete(path="/{user_id", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def delete_user(
        user_id: UUID,
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    try:
        user = await users_service.delete_user(user_id)
        return user
    except UserNotFoundError:
        raise HTTPException(
            detail="user not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

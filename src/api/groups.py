from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from exceptions import (
    GroupNotFoundError,
    UserGroupAttachError,
    UserGroupDetachError
)
from schemas import (
    GroupSchema,
    GroupItemsSchema,
    GroupUsersSchema,
    GroupTasksSchema,
    GroupSchemaCreate,
    GroupSchemaUpdate,
    UserGroupSchemaAttach
)
from services import GroupsService
from .dependencies import get_groups_service


router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupSchema, status_code=status.HTTP_201_CREATED)
async def create_group(
        data: GroupSchemaCreate,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        return await groups_service.create_group(data)
    except UserGroupAttachError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user does not exist"
        )


@router.get("/{group_id}", response_model=GroupSchema, status_code=status.HTTP_200_OK)
async def get_group_basic(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        return await groups_service.get_group_basic(group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.get("/{group_id}/details", response_model=GroupItemsSchema, status_code=status.HTTP_200_OK)
async def get_group_details(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        return await groups_service.get_group_details(group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.get("/{group_id}/users", response_model=GroupUsersSchema, status_code=status.HTTP_200_OK)
async def get_group_users(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        return await groups_service.get_group_users(group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.get("/{group_id}/tasks", response_model=GroupTasksSchema, status_code=status.HTTP_200_OK)
async def get_group_tasks(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        return await groups_service.get_group_tasks(group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.patch("/{group_id}", response_model=GroupSchema, status_code=status.HTTP_200_OK)
async def update_group(
        group_id: UUID,
        data: GroupSchemaUpdate,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        return await groups_service.update_group(group_id, data)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.delete("/{group_id}", response_model=GroupSchema, status_code=status.HTTP_200_OK)
async def delete_group(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        return await groups_service.delete_group(group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.post("/{group_id}/users", status_code=status.HTTP_204_NO_CONTENT)
async def add_user_to_group(
        group_id: UUID,
        data: UserGroupSchemaAttach,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        await groups_service.add_user_to_group(group_id, data)
    except UserGroupAttachError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot add user to group"
        )


@router.delete("/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_group(
        group_id: UUID,
        user_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        await groups_service.remove_user_from_group(group_id, user_id)
    except UserGroupDetachError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot remove user from group"
        )

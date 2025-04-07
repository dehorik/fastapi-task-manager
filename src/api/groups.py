from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from exceptions import (
    GroupNotFoundError,
    NonExistentUserError,
    UserGroupAttachError,
    UserGroupDetachError
)
from schemas import (
    GroupSchema,
    GroupItemsSchema,
    GroupSchemaCreate,
    GroupSchemaUpdate,
    UserGroupSchemaAttach
)
from services import GroupsService
from .dependencies import get_groups_service


router = APIRouter(prefix="/groups", tags=["groups"])


@router.post(
    path="",
    response_model=GroupSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_group(
        data: GroupSchemaCreate,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        group = await groups_service.create_group(data)
        return group
    except NonExistentUserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the given user_id does not exist"
        )


@router.get(
    path="/{group_id}",
    response_model=GroupSchema,
    status_code=status.HTTP_200_OK
)
async def get_group(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        group = await groups_service.get_group(group_id)
        return group
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.get(
    path="/{group_id}/details",
    response_model=GroupItemsSchema,
    status_code=status.HTTP_200_OK
)
async def get_full_group_data(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        group = await groups_service.get_full_group_data(group_id)
        return group
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.patch(
    path="/{group_id}",
    response_model=GroupSchema,
    status_code=status.HTTP_200_OK
)
async def update_group(
        group_id: UUID,
        data: GroupSchemaUpdate,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        group = await groups_service.update_group(group_id, data)
        return group
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.delete(
    path="/{group_id}",
    response_model=GroupSchema,
    status_code=status.HTTP_200_OK
)
async def delete_group(
        group_id: UUID,
        groups_service: Annotated[GroupsService, Depends(get_groups_service)]
):
    try:
        group = await groups_service.delete_group(group_id)
        return group
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.post(
    path="/{group_id}/users",
    status_code=status.HTTP_204_NO_CONTENT
)
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


@router.delete(
    path="/{group_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_user_form_group(
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

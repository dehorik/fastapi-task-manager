from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from auth import TokenPayloadSchema, verify_token
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


@router.post(
    "",
    response_model=GroupSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_group(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        data: GroupSchemaCreate,
):
    try:
        return await groups_service.create_group(payload, data)
    except UserGroupAttachError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user does not exist"
        )


@router.get(
    "/{group_id}",
    response_model=GroupSchema,
    status_code=status.HTTP_200_OK
)
async def get_group_basic(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID
):
    try:
        return await groups_service.get_group_basic(payload, group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.get(
    "/{group_id}/details",
    response_model=GroupItemsSchema,
    status_code=status.HTTP_200_OK
)
async def get_group_details(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID,
):
    try:
        return await groups_service.get_group_details(payload, group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.get(
    "/{group_id}/users",
    response_model=GroupUsersSchema,
    status_code=status.HTTP_200_OK
)
async def get_group_users(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID
):
    try:
        return await groups_service.get_group_users(payload, group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.get(
    "/{group_id}/tasks",
    response_model=GroupTasksSchema,
    status_code=status.HTTP_200_OK
)
async def get_group_tasks(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID
):
    try:
        return await groups_service.get_group_tasks(payload, group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.patch(
    "/{group_id}",
    response_model=GroupSchema,
    status_code=status.HTTP_200_OK
)
async def update_group(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID,
        data: GroupSchemaUpdate
):
    try:
        return await groups_service.update_group(payload, group_id, data)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.delete(
    "/{group_id}",
    response_model=GroupSchema,
    status_code=status.HTTP_200_OK
)
async def delete_group(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID
):
    try:
        return await groups_service.delete_group(payload, group_id)
    except GroupNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="group not found"
        )


@router.post("/{group_id}/users", status_code=status.HTTP_204_NO_CONTENT)
async def add_user_to_group(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID,
        data: UserGroupSchemaAttach
):
    try:
        await groups_service.add_user_to_group(payload, group_id, data)
    except UserGroupAttachError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot add user to group"
        )


@router.delete(
    "/{group_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_user_from_group(
        payload: Annotated[TokenPayloadSchema, Depends(verify_token)],
        groups_service: Annotated[GroupsService, Depends(get_groups_service)],
        group_id: UUID,
        user_id: UUID,
):
    try:
        await groups_service.remove_user_from_group(payload, group_id, user_id)
    except UserGroupDetachError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot remove user from group"
        )

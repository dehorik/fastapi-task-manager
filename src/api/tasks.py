from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from exceptions import TaskNotFoundError, NonExistentGroupError
from schemas import TaskSchema, TaskSchemaCreate, TaskSchemaUpdate
from services import TasksService
from .dependencies import get_tasks_service


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
        data: TaskSchemaCreate,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        return await tasks_service.create_task(data)
    except NonExistentGroupError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="group does not exist"
        )


@router.get("/{task_id}", response_model=TaskSchema, status_code=status.HTTP_200_OK)
async def get_task(
        task_id: UUID,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        return await tasks_service.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found"
        )


@router.patch("/{task_id}", response_model=TaskSchema, status_code=status.HTTP_200_OK)
async def update_task(
        task_id: UUID,
        data: TaskSchemaUpdate,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        return await tasks_service.update_task(task_id, data)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found"
        )


@router.delete("/{task_id}", response_model=TaskSchema, status_code=status.HTTP_200_OK)
async def delete_task(
        task_id: UUID,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        return await tasks_service.delete_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found"
        )

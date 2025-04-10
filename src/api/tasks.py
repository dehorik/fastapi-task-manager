from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from exceptions import TaskNotFoundError, NonExistentGroupError
from schemas import TaskSchema, TaskSchemaCreate, TaskSchemaUpdate
from services import TasksService
from .dependencies import get_tasks_service


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    path="",
    response_model=TaskSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
        data: TaskSchemaCreate,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        task = await tasks_service.create_task(data)
        return task
    except NonExistentGroupError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group with the given group_id does not exist"
        )


@router.get(
    path="/{task_id}",
    response_model=TaskSchema,
    status_code=status.HTTP_200_OK
)
async def get_task(
        task_id: UUID,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        task = await tasks_service.get_task(task_id)
        return task
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found"
        )


@router.patch(
    path="/{task_id}",
    response_model=TaskSchema,
    status_code=status.HTTP_200_OK
)
async def update_task(
        task_id: UUID,
        data: TaskSchemaUpdate,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        task = await tasks_service.update_task(task_id, data)
        return task
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found"
        )


@router.delete(
    path="/{task_id}",
    response_model=TaskSchema,
    status_code=status.HTTP_200_OK
)
async def delete_task(
        task_id: UUID,
        tasks_service: Annotated[TasksService, Depends(get_tasks_service)]
):
    try:
        task = await tasks_service.delete_task(task_id)
        return task
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found"
        )

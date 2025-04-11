from uuid import UUID

from sqlalchemy.exc import IntegrityError

from exceptions import NonExistentGroupError, TaskNotFoundError, ResultNotFound
from interfaces import AbstractUnitOfWork
from schemas import TaskSchema, TaskSchemaCreate, TaskSchemaUpdate


class TasksService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_task(self, data: TaskSchemaCreate) -> TaskSchema:
        try:
            async with self.uow as uow:
                task = await uow.tasks.create(data.model_dump())
                await uow.commit()

            return TaskSchema.model_validate(task, from_attributes=True)
        except IntegrityError:
            raise NonExistentGroupError("group does not exist")

    async def get_task(self, task_id: UUID) -> TaskSchema:
        async with self.uow as uow:
            task = await uow.tasks.get(task_id)

        if task is None:
            raise TaskNotFoundError("task not found")

        return TaskSchema.model_validate(task, from_attributes=True)

    async def update_task(self, task_id: UUID, data: TaskSchemaUpdate) -> TaskSchema:
        try:
            async with self.uow as uow:
                task = await uow.tasks.update(
                    task_id,
                    {
                        key: value
                        for key, value in data.model_dump().items()
                        if value is not None
                    }
                )
                await uow.commit()

            return TaskSchema.model_validate(task, from_attributes=True)
        except ResultNotFound:
            raise TaskNotFoundError("task not found")

    async def delete_task(self, task_id: UUID) -> TaskSchema:
        try:
            async with self.uow as uow:
                task = await uow.tasks.delete(task_id)
                await uow.commit()

            return TaskSchema.model_validate(task, from_attributes=True)
        except ResultNotFound:
            raise TaskNotFoundError("task not found")

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from auth import TokenPayloadSchema
from exceptions import NonExistentGroupError, TaskNotFoundError, ResultNotFound
from interfaces import AbstractUnitOfWork
from schemas import TaskSchema, TaskSchemaCreate, TaskSchemaUpdate


class TasksService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @staticmethod
    async def _check_user_access_to_task(
            uow: AbstractUnitOfWork,
            user_id: UUID,
            task_id: UUID
    ) -> bool:
        """
        Проверка присутствия пользователя с user_id в группе,
        к которой относится задача с task_id, с целью узнать, имеет лм право
        данный пользователь на изменение задач в этой группе

        :param uow: объект unit of work с открытой сессией
        (объект нужно открыть через асинхронный контекстный менеджер)
        :param user_id: user_id проверяемого пользователя
        :param task_id: task_id задачи, которая должна относиться
        к одной из групп из списка групп пользователя
        :return: True/False в зависимости от результата проверки
        """

        return bool(await uow.tasks.get_task_id_if_user_in_group(user_id, task_id))

    async def create_task(
            self,
            payload: TokenPayloadSchema,
            data: TaskSchemaCreate
    ) -> TaskSchema:
        try:
            async with self.uow as uow:
                if await uow.groups.get_group_id_if_user_in_group(payload.sub, data.group_id):
                    task = await uow.tasks.create(data.model_dump())
                    await uow.commit()
                else:
                    raise NonExistentGroupError("group does not exist")

            return TaskSchema.model_validate(task, from_attributes=True)
        except IntegrityError:
            raise NonExistentGroupError("group does not exist")

    async def get_task(
            self,
            payload: TokenPayloadSchema,
            task_id: UUID
    ) -> TaskSchema:
        async with self.uow as uow:
            if await self._check_user_access_to_task(uow, payload.sub, task_id):
                task = await uow.tasks.get(task_id)
            else:
                raise TaskNotFoundError("task not found")

        if task is None:
            raise TaskNotFoundError("task not found")

        return TaskSchema.model_validate(task, from_attributes=True)

    async def update_task(
            self,
            payload: TokenPayloadSchema,
            task_id: UUID,
            data: TaskSchemaUpdate
    ) -> TaskSchema:
        try:
            async with self.uow as uow:
                if await self._check_user_access_to_task(uow, payload.sub, task_id):
                    task = await uow.tasks.update(
                        task_id,
                        data.model_dump(exclude_none=True)
                    )
                    await uow.commit()
                else:
                    raise TaskNotFoundError("task not found")

            return TaskSchema.model_validate(task, from_attributes=True)
        except ResultNotFound:
            raise TaskNotFoundError("task not found")

    async def delete_task(
            self,
            payload: TokenPayloadSchema,
            task_id: UUID
    ) -> TaskSchema:
        try:
            async with self.uow as uow:
                if await self._check_user_access_to_task(uow, payload.sub, task_id):
                    task = await uow.tasks.delete(task_id)
                    await uow.commit()
                else:
                    raise TaskNotFoundError("task not found")

            return TaskSchema.model_validate(task, from_attributes=True)
        except ResultNotFound:
            raise TaskNotFoundError("task not found")

from uuid import UUID

from sqlalchemy import select

from models import Task, Group, UsersGroups
from .sqlalchemy_repository import SQLAlchemyRepository


class TasksRepository(SQLAlchemyRepository):
    """Реализация репозитория для работы с задачами"""

    model = Task

    async def get_task_id_if_user_in_group(
            self,
            user_id: UUID,
            task_id: UUID
    ) -> UUID | None:
        """
        Метод проверяет, является ли задача с task_id одной из задач,
        которые относятся к одной из групп пользователя с user_id.
        Если проверка проходит, переданный task_id возвращается, иначе None
        """

        task_id = await self.session.execute(
            select(Task.task_id)
            .join(Group)
            .join(UsersGroups)
            .where(UsersGroups.user_id == user_id, Task.task_id == task_id)
        )
        return task_id.scalar_one_or_none()

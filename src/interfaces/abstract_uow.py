from abc import ABC, abstractmethod
from typing import Any


class AbstractUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, *args):
        pass

    @abstractmethod
    async def commit(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def rollback(self, *args, **kwargs) -> Any:
        pass

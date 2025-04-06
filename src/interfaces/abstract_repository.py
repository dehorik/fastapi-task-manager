from abc import ABC, abstractmethod
from typing import Any


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def get(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def update(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def remove(self, *args, **kwargs) -> Any:
        pass

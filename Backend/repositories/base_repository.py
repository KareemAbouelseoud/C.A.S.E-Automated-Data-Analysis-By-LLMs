# repositories/base_repository.py
from abc import ABC, abstractmethod
import os
from typing import List, Optional, Generic, TypeVar
from motor.motor_asyncio import AsyncIOMotorClient

T = TypeVar('T') # Generic Type Variable

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def __init__(self, collection_name: str):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
        self.database = self.client[os.getenv("DATABASE_NAME")]
        self.collection = self.database[collection_name]

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def update(self, id: str, entity: T) -> bool:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
    @abstractmethod
    async def Filter(self, filters:dict) -> List[T]:
        pass
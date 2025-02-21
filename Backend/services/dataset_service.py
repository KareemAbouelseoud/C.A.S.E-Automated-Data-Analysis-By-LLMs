from typing import List, Optional

from dataModels.project import Dataset
from repositories.dataset_repository import DatasetRepository

class DatasetService:
    def __init__(self, dataset_repository: DatasetRepository):
        self.dataset_repository = dataset_repository

    async def get_dataset(self, id: str) -> Optional[Dataset]:
        return await self.dataset_repository.get_by_id(id)

    async def get_datasets(self) -> List[Dataset]:
        return await self.dataset_repository.get_all()

    async def create_dataset(self, dataset: Dataset) -> Dataset:
        return await self.dataset_repository.create(dataset)

    async def update_dataset(self, id: str, dataset: Dataset) -> bool:
        return await self.dataset_repository.update(id, dataset)

    async def delete_dataset(self, id: str) -> bool:
        return await self.dataset_repository.delete(id)

from typing import Optional, List

from bson.objectid import ObjectId

from .base_repository import BaseRepository
from dataModels.project import Dataset

class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, database):
        super().__init__("datasets", database)

    async def get_by_id(self, id: str) -> Optional[Dataset]:
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            return Dataset.from_dict(document)
        return None

    async def get_all(self) -> List[Dataset]:
        datasets = []
        async for document in self.collection.find():
            datasets.append(Dataset.from_dict(document))
        return datasets

    async def create(self, dataset: Dataset) -> Dataset:
        result = await self.collection.insert_one(dataset.to_dict())
        dataset.id = str(result.inserted_id)
        return dataset

    async def update(self, id: str, dataset: Dataset) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": dataset.to_dict()})
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
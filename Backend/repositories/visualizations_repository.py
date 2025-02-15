from typing import Optional, List

from bson.objectid import ObjectId

from .base_repository import BaseRepository
from dataModels.visualization import visualizations

class VisualizationRepository(BaseRepository[visualizations]):
    def __init__(self):
        super().__init__("Visualizations")

    async def get_by_project_id(self, project_id: str) -> Optional[visualizations]:
        document = await self.collection.find_one({"project_id": project_id})
        if document:
            return visualizations.from_mongo(document)
        return None
    
    async def create(self,project_id:str,user_id:str) -> str:
        new_Item=visualizations(project_id=project_id,user_id=user_id)
        result = await self.collection.insert_one(new_Item.model_dump(exclude={"id"}))
        new_Item.id = str(result.inserted_id)
        return new_Item.id

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def update(self, id: str, visualizations:visualizations) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": visualizations.model_dump(exclude={"id"})})
        return result.modified_count > 0
    
    async def get_by_id(self, id: str) -> Optional[visualizations]:
        pass
    async def get_all(self) -> List[visualizations]:
        pass
    async def Filter(self, filters:dict) -> List[visualizations]:
        pass
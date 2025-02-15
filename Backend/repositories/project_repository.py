from typing import Optional, List

from bson.objectid import ObjectId

from .base_repository import BaseRepository
from dataModels.project import Project
from .user_repository import UserRepository
class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__("projects")
        

    async def get_by_id(self, id: str) -> Optional[Project]:
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            project=Project.from_mongo(document)
            project.id=str(project.id)
            return project
        return None

    
    async def Filter(self, filter: dict) -> List[Project]:
        filtered_Items = []
        async for document in self.collection.find(filter):
            project=Project.from_mongo(document)
            project.id=str(project.id)
            filtered_Items.append(project.model_dump())  # Convert ObjectId
        return filtered_Items

    
    async def get_all(self) -> List[Project]:
        projects = []
        async for document in self.collection.find():
            projects.append(Project(**document))
        return projects

    async def create(self, project: Project) -> Project:
        result = await self.collection.insert_one(project.model_dump(exclude={"id"}))
        project.id = str(result.inserted_id)
        
        return project

    async def update(self, id: str, project: Project) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": project.model_dump(exclude={"id"})})
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0


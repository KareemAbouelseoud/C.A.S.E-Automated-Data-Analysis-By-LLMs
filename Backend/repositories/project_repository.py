# repositories/project_repository.py
from typing import Optional, List

from bson.objectid import ObjectId

from .base_repository import BaseRepository
from dataModels.project import Project

class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__("projects")

    async def get_by_id(self, id: str) -> Optional[Project]:
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            return Project.from_dict(document)
        return None
    
    async def Filter(self,filter:dict)->List[Project]:
            filtered_Items=[]
            async for document in self.collection.find(filter):
                filtered_Items.append(Project.from_dict(document))
            return filtered_Items
    
    async def get_all(self) -> List[Project]:
        projects = []
        async for document in self.collection.find():
            projects.append(Project.from_dict(document))
        return projects

    async def create(self, project: Project) -> Project:
        result = await self.collection.insert_one(project.to_dict())
        project.id = str(result.inserted_id)
        return project

    async def update(self, id: str, project: Project) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": project.to_dict()})
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0


from typing import List, Optional

from dataModels.project import Project
from repositories.project_repository import ProjectRepository

class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def get_project(self, id: str) -> Optional[Project]:
        return await self.project_repository.get_by_id(id)

    async def get_projects(self,userId:str) -> List[Project]:
        return await self.project_repository.Filter({"user_id":userId})

    async def create_project(self, project: Project) -> Project:
        return await self.project_repository.create(project)

    async def update_project(self, id: str, project: Project) -> bool:
        return await self.project_repository.update(id, project)

    async def delete_project(self, id: str) -> bool:
        return await self.project_repository.delete(id)


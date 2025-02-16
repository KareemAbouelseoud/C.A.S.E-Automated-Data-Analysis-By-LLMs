from config import *
from Agents.codeGeneration import pipeline 
def get_repo():
    repo = VisualizationRepository()
    return repo

class visualizationsService:
    def __init__(self):
        self.viz_repository = get_repo()
        self.project_repository = ProjectRepository()
    
    #region Vizualizations Get functions
    
    async def get_project_Visualizations(self, project_id: str) -> Optional[visualizations]:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")

        return project_Visualizations.model_dump()

    async def get_Auto_Gen_Viz(self,project_id:str) -> List[str]:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        return project_Visualizations.Auto_generated_viz
    
    async def get_Chat_Viz(self,project_id:str) -> List[str]:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        return project_Visualizations.Auto_generated_viz
    #endregion    
    
    #region Vizualizations Update functions
    
    async def update_Chat_Viz(self, project_id: str, new_viz: ChatViz) -> bool:
        if new_viz==None:
            raise HTTPException(status_code=500, detail=f"Can not insert a None Visualization into MongoDB: {e}")
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Chat_visualizations.append(new_viz)
        try:
            return await self.viz_repository.update(id, project_Visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    
    async def update_Auto_Gen_Viz(self, project_id: str) -> Tuple[bool, List[str]]:
        visualizations = await pipeline.generate_visualizations(project_id)
        serializable_visualizations = [make_serializable(v) for v in visualizations]
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Auto_generated_viz=serializable_visualizations
        try:
            return (await self.viz_repository.update(project_id, project_Visualizations),serializable_visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    #endregion
    
    #region Vizualizations Clear functions
    async def clear_Auto_Gen_Viz(self, project_id: str) -> bool:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Auto_generated_viz=[]
        try:
            return await self.viz_repository.update(id, project_Visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    
    async def clear_Chat_Viz(self, project_id: str) -> bool:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Chat_visualizations=[]
        try:
            return await self.viz_repository.update(id, project_Visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    #endregion
    
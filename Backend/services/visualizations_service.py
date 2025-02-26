from config import *
import requests
def get_repo():
    repo = VisualizationRepository()
    return repo
class visualizationsService:
    def __init__(self):
        self.viz_repository = get_repo()
        self.project_repository = ProjectRepository()
        self.project_service=ProjectService()
        self.url="http://Agents:8006"

    
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
        return project_Visualizations.Chat_visualizations
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
        project_Visualizations.Chat_visualizations.append(new_viz.viz)
        try:
            return await self.viz_repository.update(project_id, project_Visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    
    async def update_Auto_Gen_Viz(self, project_id: str) -> Tuple[bool, List[str]]:
        try:
            dataframe=(await self.project_service.fetch_dataset(project_id)).to_json()
            data_report=await self.project_service.fetch_data_report(project_id)

            response=requests.post(f"{self.url}/visualizations/createDashboard",json={'dataframe':dataframe, 'data_report':data_report})
            serializable_visualizations=json.loads(response.json())['visualizations']
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error from Agents Module: {e}")
        
        print("THIS IS SERIALIZABLE VISUALIZATION IN VIZ SERVICE",len(serializable_visualizations))
        print("THIS IS SERIALIZABLE VISUALIZATION IN VIZ SERVICE",type(serializable_visualizations))
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
    
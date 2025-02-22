
from config import *
def get_repo():
    repo = ProjectRepository()
    return repo
class ProjectService:
    def __init__(self):
        self.project_repository = get_repo()
        self.userRepository = UserRepository()
        self.vizRepository= VisualizationRepository()
    #region Project functions

    async def get_project(self, id: str) -> Optional[Project]:
        project=await self.project_repository.get_by_id(id)
        return project.model_dump()

    async def get_user_projects(self,userId:str) -> List[Project]:
        projects=await self.project_repository.Filter({"user_id":userId})
        return projects

    async def create_project(self,file:UploadFile = File(...), user_id: str = Form(...), name: str = Form(...)) -> Project:
        # 0. Check if user exist already
        user = await self.userRepository.get_by_id(user_id) 
        if user==None:
            raise HTTPException(status_code=400, detail="Invalid user_Id Please provide an existing user id.")
        # 1. Validate file type (ensure it's a CSV)
        if file.filename[-4:].lower().strip() != ".csv":
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
        # 2. Read the CSV file content
        contents = await file.read()
        decoded_contents = contents.decode('utf-8') # Decode bytes to string
        # 3. Convert CSV to JSON using pandas
        try:
            df = pd.read_csv(io.StringIO(decoded_contents))  # Read from string buffer
            dataframe = df.to_json(orient="records") # If you want a raw JSON string
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error converting CSV to JSON: {e}")
        
        new_project = Project(name=name, user_id=user_id,Dataset=dataframe,created_Date=datetime.now())
        new_project.model_Chat=projectChat(last_update=datetime.now())
        new_project.streamlit_Chat=projectChat(last_update=datetime.now())
        ## BUG: The below code is for testing purposes only we will remove it later
        with open(r"F:\00000000 GP\C.A.S.E-Automated-Data-Analysis-By-LLMs\Database\dataReports\data_report_1.json", 'r') as file:
            new_project.data_report = json.dumps(json.load(file))
        # 5.  Important: Save ٍProject to MongoDB
        try:       
            project = await self.project_repository.create(new_project)         
            if project:
                user.Projects.append(str(project.id))
                await self.userRepository.update(user_id,user)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating project and data to MongoDB: {e}")
        try:
            await self.vizRepository.create(str(project.id),user_id=user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating project visualization and data to MongoDB: {e}")

        return project
        

    async def update_project(self, id: str, project: Project) -> bool:
        return await self.project_repository.update(id, project)
    
    async def delete_project(self, id: str) -> bool:
        return await self.project_repository.delete(id)
    #endregion
    
    #region Chat Functions

    async def clearChatHistory(self, project_id: str,user_id:str) -> bool:
        try:
            user = await self.userRepository.get_by_id(user_id)  
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving user from MongoDB: {e} Maybe the user is deleted or not created yet")
        try:
            project = await self.get_project(project_id) 
            project = Project.from_dict(project)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e} Maybe the project is deleted or not created yet")
        try:
            project_viz = await self.vizRepository.get_by_project_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project visualizations from MongoDB: {e}")
            
        if user==None:
            raise HTTPException(status_code=400, detail="Invalid user_Id Please provide an existing user id.")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        if project_viz==None:
            raise HTTPException(status_code=400, detail="Project Visualization is not created in MongoDB")
        
        
        project.model_Chat=projectChat(last_update=datetime.now())
        project.streamlit_Chat=projectChat(last_update=datetime.now())
        project_viz.Chat_visualizations=[]

        try:
            await self.project_repository.update(project_id, project)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project and data to MongoDB: {e}")
        try:
            await self.vizRepository.update(project_id, project_viz)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project and data to MongoDB: {e}")
    
    async def updateChatHistory(self, project_id: str, user_id:str,last_conv:list) -> bool:
        try:
            user = await self.userRepository.get_by_id(user_id)  
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving user from MongoDB: {e}")
        try:
            project = await self.get_project(project_id)
            project= Project.from_dict(project)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if user==None:
            raise HTTPException(status_code=400, detail="Invalid user_Id Please provide an existing user id.")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        
        hist_dict={'st_history':[],'model_history':[]}
        for i,message in enumerate(last_conv):
            hist_dict['st_history'].append({'role':message['role'],'content':message['content']})
            if i==0:
                continue
            if 'visualizer'!=message['role']:
                hist_dict['model_history'].append({'role':message['role'],'content':message['content']})
        project.model_Chat=projectChat()
        project.streamlit_Chat=projectChat()
        project.model_Chat.messages=json.dumps(hist_dict['model_history'])
        project.streamlit_Chat.messages=json.dumps(hist_dict['st_history'])
        
        project.model_Chat.last_update=datetime.now()
        project.streamlit_Chat.last_update=datetime.now()
        
        try:
            await self.project_repository.update(project.id, project)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project's chat to MongoDB: {e}")
    
    async def get_model_chat_history(self, project_id: str) -> Optional[List[str]]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        if project.model_Chat.messages==None:
            return []
        return json.loads(project.model_Chat.messages)
    
    async def get_streamlit_chat_history(self, project_id: str) -> Optional[Project]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        if project.streamlit_Chat.messages==None:
            return '[]'
        return project.streamlit_Chat.messages
    #endregion

    #region other fetches
    async def fetch_data_report(self, project_id: str) -> Optional[str]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        return project.data_report
    
    async def fetch_dataset(self, project_id: str) -> Optional[str]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        return pd.read_json(StringIO(project.Dataset))

    #endregion

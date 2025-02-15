from config import *
def get_repo():
    repo = ProjectRepository()
    return repo
class ProjectService:
    def __init__(self):
        self.project_repository = get_repo()
        self.userRepository = UserRepository()

    async def get_project(self, id: str) -> Optional[Project]:
        project=await self.project_repository.get_by_id(id)
        return project.model_dump()

    async def get_user_projects(self,userId:str) -> List[Project]:
        projects=await self.project_repository.Filter({"user_id":userId})
        return projects

    async def create_project(self,file:UploadFile = File(...), user_id: str = Form(...), name: str = Form(...)) -> Project:
        # 0. Check if user exist already
        user = await self.userRepository.get_by_id(user_id) 
        # 1. Validate file type (ensure it's a CSV)
        if file.content_type != "text/csv":
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
        
        new_project = Project(name=name, user_id=user_id,Dataset=dataframe)
        # 5.  Important: Save ٍProject to MongoDB
        try:       
            project = await self.project_repository.create(new_project)         
            if project:
                user.Projects.append(str(project.id))
                await self.userRepository.update(user_id,user)
            return project

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving project and data to MongoDB: {e}")
        

    async def update_project(self, id: str, project: Project) -> bool:
        return await self.project_repository.update(id, project)
    
    async def clearChatHistory(self, id: str, project: Project) -> bool:
        project.project_Chat=None
        return await self.project_repository.update(id, project)

    async def delete_project(self, id: str) -> bool:
        return await self.project_repository.delete(id)


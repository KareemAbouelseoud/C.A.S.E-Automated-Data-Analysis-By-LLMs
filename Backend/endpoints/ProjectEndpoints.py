from config import *
#######################################


# Dependency Injection Function
def get_project_service():
    service = ProjectService()
    return service

class UserRouter:
    router = APIRouter()

    def __init__(self, project_service:  ProjectService= Depends(get_project_service)):
        self.project_service = project_service
    @router.post("/createProject")
    async def upload_file(self,file: UploadFile = File(...), user_id: str = Form(...), name: str = Form(...)):
        """
        API endpoint to receive and save uploaded files.
        """
        if user_id=="" | name=="":
            raise HTTPException(status_code=400, detail="Invalid Inputs. Either the user_id or the name is null.")
        try:
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

            
            new_project = Project(name=name, user_id=user_id)
            
            # 5.  Important: Save the project and the JSON data
            try:                
                new_project.data = dataframe # Store the JSON data within the project
                created_project = await self.project_service.create_project(new_project)

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error saving project and data to MongoDB: {e}")

            # 6. Return the created project (or a success message)
            return {"message": "File uploaded and processed successfully!", "project_id": str(created_project.id)}

        except HTTPException as http_ex:
            # Re-raise HTTPExceptions
            raise http_ex
        except Exception as e:
            # Handle unexpected errors
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    @router.get("/readProjects/{user_id}")
    async def readProjects(self,user_id:str):
        """
        API endpoint to receive and save uploaded files.
        """
        return json.dumps({'data':self.project_service.get_projects(user_id)})
    @router.get("/projectDetails/{project_id}")
    async def getProject(self,project_id:str):
        """
        API endpoint to receive and save uploaded files.
        """
        return json.dumps({'data':self.project_service.get_project(project_id)})

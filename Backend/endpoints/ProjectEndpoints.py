from config import *
import asyncio
#######################################


# Dependency Injection Function
def get_project_service():
    service = ProjectService()
    return service


Project_router = APIRouter()


project_service = get_project_service()
@Project_router.post("/project",tags=["Project"])
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...), name: str = Form(...)):
    """
    API endpoint to receive and save uploaded files.
    """
    if user_id=="" or name=="":
        raise HTTPException(status_code=400, detail="Invalid Inputs. Either the user_id or the name is null.")
    try:
        # Create the project asynchronously
        asyncio.create_task(project_service.create_project(file, user_id, name))
    except HTTPException as http_ex:
        # Re-raise HTTPExceptions
        raise http_ex
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@Project_router.get("/project/GetProjects/{user_id}",tags=["Project"])
async def readProjects(user_id:str):
    """
    API endpoint to receive and save uploaded files.
    """
    try:
        return json.dumps({'data':await project_service.get_user_projects(user_id)})
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
@Project_router.get("/project/projectDetails/{project_id}",tags=["Project"])
async def getProject(project_id:str):
    """
    API endpoint to receive and save uploaded files.
    """
    return json.dumps({'data':await project_service.get_project(project_id)})



@Project_router.get("/project/{project_id}/fetchDataset",tags=["Project"])
async def fetchDataset(project_id:str):
    """
    API endpoint to receive and save uploaded files.
    """
    df = await project_service.fetch_dataset(project_id)
    
    return {'data':df.to_json()}


@Project_router.get("/project/{project_id}/fetchDataReport",tags=["Project"])
async def fetchDataReport(project_id:str):
    """
    API endpoint to receive and save uploaded files.
    """
    dr = await project_service.fetch_data_report(project_id)
    
    return {'data':dr}

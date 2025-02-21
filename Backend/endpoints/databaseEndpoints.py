from config import *
db_router = APIRouter()



@db_router.post('/login')
async def login(body: LoginRequest):
    """
    Endpoint to validate user login credentials.

    Args:
        body (LoginRequest): Request body containing username and password.

    Returns:
        dict: JSON with login status.
    """
    return {'data':str(mainDatabase.check_login(body.username,body.password))}

@db_router.get('/get_id/{username}')
async def get_id(username: str):
    """
    Endpoint to retrieve user ID based on username.

    Args:
        username (str): Username to retrieve user ID for.

    Returns:
        dict: JSON with user ID.
    """
    return {'data':str(mainDatabase.get_user_id(username))}

@db_router.post('/signup')
async def Signup(body: SignUpRequest):
    """
    Endpoint to register a new user.

    Args:
        body (SignUpRequest): Request body containing user details.

    Returns:
        dict: JSON with signup status.
    """
    return {'data':mainDatabase.signup(
                            first_name=body.first_name,
                            last_name=body.last_name,
                            email=body.email,
                            username=body.username,
                            password=body.password
                            )
            }

@db_router.get('/get_name/{user_id}')
async def get_name(user_id: str):
    """
    Endpoint to fetch first name of user account

    Args:
        user_id (str): The user's Id.


    Returns:
        str
            First Name
    """
    return {'data':mainDatabase.fetch_name(user_id)}


@db_router.get('/get_username/{user_id}')
async def get_username(user_id: str):
    """
    Endpoint to fetch Username of user account

    Args:
        user_id (str): The user's Id.


    Returns:
        str
            Username
    """
    return {'data':mainDatabase.fetch_username(user_id)}

@db_router.get('/get_email/{user_id}')
async def get_email(user_id: str):
    """
    Endpoint to fetch Username of user account

    Args:
        user_id (str): The user's Id.


    Returns:
        str
            Username
    """
    return {'data':mainDatabase.fetch_email(user_id)}



@db_router.post("/createProject")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...), name: str = Form(...)):
    """
    API endpoint to receive and save uploaded files.
    """
    mainDatabase.create_project(name,user_id,file)

@db_router.get("/readProjects/{user_id}")
async def readProjects(user_id:str):
    """
    API endpoint to receive and save uploaded files.
    """
    return json.dumps({'data':mainDatabase.read_projects(user_id)})


@db_router.get("/projectDetails/{project_id}")
async def getProject(project_id:str):
    """
    API endpoint to receive and save uploaded files.
    """
    return json.dumps({'data':mainDatabase.get_project(project_id)})



@db_router.get("/fetchDataset/{project_id}")
async def getProject(project_id:str):
    """
    API endpoint to receive and save uploaded files.
    """
    return {'data':mainDatabase.fetch_dataset(project_id).to_json()}




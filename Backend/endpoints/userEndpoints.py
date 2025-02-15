from config import *
#######################################


# Dependency Injection Function
def getuser_service():
    service = UserService()
    return service

user_service =getuser_service()
user_router = APIRouter()

@user_router.post('/user/login',tags=["users"])
async def login(body: LoginRequest):
    """
    Endpoint to validate user login credentials.

    Args:
        body (LoginRequest): Request body containing username and password.

    Returns:
        dict: JSON with login status.
    """
    return {'data':str(await user_service.check_login(body.username,body.password))}

@user_router.get('/user/get_id/{username}',tags=["users"])
async def get_id(username: str):
    """
    Endpoint to retrieve user ID based on username.

    Args:
        username (str): Username to retrieve user ID for.

    Returns:
        dict: JSON with user ID.
    """
    return {'data':str(await user_service.get_user_id(username))}
@user_router.post('/user/signup',tags=["users"])
async def Signup(body: SignUpRequest):
    """
    Endpoint to register a new user.

    Args:
        body (SignUpRequest): Request body containing user details.

    Returns:
        dict: JSON with signup status.
    """
    return {'data':await user_service.create_user(body)}

@user_router.get('/user/get_name/{user_id}',tags=["users"])
async def get_name(user_id: str):
    """
    Endpoint to fetch first name of user account

    Args:
        user_id (str): The user's Id.


    Returns:
        str
            First Name
    """
    user = await  user_service.get_user(user_id)
    return {'data': user.first_name if user!=None else None}

@user_router.get('/user/get_username/{user_id}',tags=["users"])
async def get_username(user_id: str):
    """
    Endpoint to fetch Username of user account

    Args:
        user_id (str): The user's Id.


    Returns:
        str
            Username
    """
    user = await user_service.get_user(user_id)
    return {'data': user.username if user!=None else None}
@user_router.get('/user/get_email/{user_id}',tags=["users"])
async def get_email(user_id: str):
    """
    Endpoint to fetch Email of user account

    Args:
        user_id (str): The user's Id.


    Returns:
        str
            Email
    """
    user = await user_service.get_user(user_id)
    return {'data': user.email if user!=None else None}
@user_router.get('/user/get_user/{user_id}',tags=["users"])
async def get_user(user_id: str):
    """
    Endpoint to fetch user account

    Args:
        user_id (str): The user's Id.


    Returns:
        User
            User
    """
    user = await user_service.get_user(user_id)
    return {'data': user}

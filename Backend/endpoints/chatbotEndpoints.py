from config import *

project_service = ProjectService()

chatbot_router = APIRouter()

@chatbot_router.post('/chat',tags=["Chat"])
async def chat(body:Chat):
    messages=await project_service.get_model_chat_history(body.project_id)
    messages.append({"role": "user", "content": body.prompt})
    return StreamingResponse(chatbot_pipeline.chat(body.project_id,messages),media_type="text/event-stream")
    
@chatbot_router.post("/recommend",tags=["Chat"])
async def recommend(item: Recommender):

    prompt = item.prompt
    project_id = item.project_id

    return {"data":json.dumps(await recommender.recommender(json.loads(prompt),project_id))}

@chatbot_router.get('/project/{project_id}/get_model_history',tags=["Chat"])
async def get_model_history(project_id: str):
    """
    Endpoint to retrieve Streamlit chat history for a specific chat ID.

    Args:
        project_id (str): Chat ID to retrieve Streamlit chat history for.

    Returns:
        dict: JSON with Streamlit chat history.
    """
    return json.dumps({'data':await project_service.get_model_chat_history(project_id)})

@chatbot_router.get('/project/{project_id}/get_streamlit_history',tags=["Chat"])
async def get_streamlit_history(project_id: str):
    """
    Endpoint to retrieve Streamlit chat history for a specific chat ID.

    Args:
        project_id (str): Chat ID to retrieve Streamlit chat history for.

    Returns:
        str : Streamlit chat history.
    """
    return {'data':await project_service.get_streamlit_chat_history(project_id)}


@chatbot_router.post("/project/{project_id}/chat_streamlit",tags=["Chat"])
async def update_user_st_history(item: StHistory,project_id:str,user_id:str):
    if project_id=="" or user_id=="":
        raise HTTPException(status_code=400, detail="Project Id and user Id Can not be null")
    project_id=item.project_id
    last_conv=json.loads(item.last_conv)
    await project_service.updateChatHistory(project_id,user_id,last_conv)

@chatbot_router.get("/project/{project_id}/chat/clear",tags=["Project","Chat"])
async def clearChatHistory(project_id:str,user_id:str):
    """
    Clears streamlit and model history for specific user project
    Args:
        project_id (str): project_id of the User

    Returns:
        True : if updated else it raise error
    """
    if project_id=="" or user_id=="":
        raise HTTPException(status_code=400, detail="Project Id and user Id Can not be null")
    return {'Updated':await project_service.clearChatHistory(project_id=project_id,user_id=user_id)}
from config import *

project_service = ProjectService()

chatbot_router = APIRouter()

@chatbot_router.post('/chat')
async def chat(item: Chat):
    prompt = item.prompt
    project_id = item.project_id
    if item.messages:
        messages=json.loads(item.messages)
        return StreamingResponse(pipeline.chat(prompt,project_id,messages),media_type="text/event-stream")
    else:
        return StreamingResponse(pipeline.chat(prompt,project_id),media_type="text/event-stream")
    
@chatbot_router.post("/recommend")
async def recommend(item: Recommender):

    prompt = item.prompt
    project_id = item.project_id

    return {"data":json.dumps(recommender.recommender(json.loads(prompt),project_id))}


@chatbot_router.get('/create_new_chat/{project_id}')
async def create_new_chat(project_id: str):
    """
    Endpoint to create a new chat session.

    Args:
        project_id (str): User ID to create a new chat session for.

    Returns:
        JSON: New chat session details.
    """
    return mainDatabase.create_new_chat_id(project_id)


@chatbot_router.get('/get_model_history/{project_id}')
async def get_model_history(project_id: str):
    """
    Endpoint to retrieve Streamlit chat history for a specific chat ID.

    Args:
        project_id (str): Chat ID to retrieve Streamlit chat history for.

    Returns:
        dict: JSON with Streamlit chat history.
    """
    return {'data':mainDatabase.get_model_chat_history(project_id)}


@chatbot_router.post("/project/{project_id}/chat_streamlit")

async def update_user_st_history(item: StHistory,project_id:str,user_id:str):
    if project_id=="" or user_id=="":
        raise HTTPException(status_code=400, detail="Project Id and user Id Can not be null")
    project_id=item.project_id
    last_conv=json.loads(item.last_conv)
    mainDatabase.update_st_chat_history(project_id,last_conv)

@chatbot_router.get("/project/{project_id}/chat/clear",tags=["Project"])
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
    return {'Updated':await project_service.clearChatHistory(project_id)}
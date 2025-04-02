from config import *
import httpx
import json
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import asyncio
url = "http://Agents:8006"

project_service = ProjectService()

chatbot_router = APIRouter()

@chatbot_router.post('/chat', tags=["Chat"])
async def chat(body: Chat):
    async def event_stream():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url + "/chat", json={'thread_id': body.thread_id, 'prompt': body.prompt}) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")
    
    
@chatbot_router.post("/recommend", tags=["Chat"])
async def recommend(item: Recommender):
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(
            url + "/recommend",
            json={"prompt": item.prompt, 'project_id': item.project_id}
        )
        data = response.json()
        recommendations = data['data']
        
        return {"data": recommendations}

@chatbot_router.get('/project/{thread_id}/get_model_history', tags=["Chat"])
async def get_model_history(thread_id: str):
    """
    Endpoint to retrieve Streamlit chat history for a specific chat ID.

    Args:
        thread_id (str): Chat ID to retrieve Streamlit chat history for.

    Returns:
        dict: JSON with Streamlit chat history.
    """
    return json.dumps({'data': await project_service.get_model_chat_history(thread_id)})

@chatbot_router.get('/project/{project_id}/get_streamlit_history', tags=["Chat"])
async def get_streamlit_history(project_id: str):
    """
    Endpoint to retrieve Streamlit chat history for a specific chat ID.

    Args:
        project_id (str): Chat ID to retrieve Streamlit chat history for.

    Returns:
        str : Streamlit chat history.
    """
    return {'data': await project_service.get_streamlit_chat_history(project_id)}

@chatbot_router.post("/project/{project_id}/chat_streamlit", tags=["Chat"])
async def update_user_st_history(item: StHistory, project_id: str, user_id: str):
    if project_id == "" or user_id == "":
        raise HTTPException(status_code=400, detail="Project Id and user Id Can not be null")
    project_id = item.project_id
    last_conv = json.loads(item.last_conv)
    # Create a background task to update chat history
    asyncio.create_task(project_service.updateChatHistory(project_id, user_id, last_conv))
    
    # Return response immediately
    return {"status": "updating chat history"}

@chatbot_router.get("/project/{project_id}/chat/clear", tags=["Project", "Chat"])
async def clearChatHistory(project_id: str, user_id: str):
    """
    Clears streamlit and model history for specific user project
    Args:
        project_id (str): project_id of the User

    Returns:
        True : if updated else it raise error
    """
    if project_id == "" or user_id == "":
        raise HTTPException(status_code=400, detail="Project Id and user Id Can not be null")
    return {'data': await project_service.clearChatHistory(project_id=project_id, user_id=user_id)}

from fastapi import APIRouter
from .dataItems import Chat,Recommender
from fastapi.responses import StreamingResponse
import json
from Chatbot import pipeline,recommender
chatbot_router = APIRouter()


@chatbot_router.post('/chat',tags=["Chat"])
async def chat(body:Chat):
    return StreamingResponse(pipeline.chat(user_input=body.prompt,thread_id=body.thread_id),media_type="text/event-stream")

    
@chatbot_router.post("/recommend",tags=["Chat"])
async def recommend(item: Recommender):
    return {"data":json.dumps(await recommender.recommender(json.loads(item.prompt),item.project_id))}
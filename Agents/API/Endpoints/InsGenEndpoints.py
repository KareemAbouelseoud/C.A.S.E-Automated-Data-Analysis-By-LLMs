from fastapi import APIRouter
from .dataItems import Chat,Recommender, Feedback
from fastapi.responses import StreamingResponse
import json
InsGen_router = APIRouter()

@InsGen_router.get("/description")
async def get_description():
    return {"description": "This is a description of the InsGen API."}

@InsGen_router.post("/description/feedback")
async def post_description(body:Feedback):
    print("This is a user feedback :",body.__str__())
    return {"feedback": body.feedback}
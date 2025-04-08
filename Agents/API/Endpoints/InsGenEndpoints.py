from fastapi import APIRouter, HTTPException
from .dataItems import Chat,Recommender, Feedback
from fastapi.responses import StreamingResponse

import json
from ..config import *
InsGen_router = APIRouter()

@InsGen_router.get("/project/{project_id}/description",tags=["insGen"])
async def get_description(project_id:str=None):
    print("ENTERING TEST")
    try:
        result = Start_Auto_InsightGen(project_id)  # This returns an async generator
        desc = await anext(result)  # Use anext() instead of __anext__()
        # print("RESULT", desc)
        return desc
    except Exception as e:
        print(f"Error in get_description: {str(e)}")
        raise
            
    except StopAsyncIteration:
        print("Generator stopped without producing description")
        raise HTTPException(
            status_code=500,
            detail="Description generation failed - no output produced"
        )
    except Exception as e:
        print(f"Error in get_description: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@InsGen_router.post("/description/feedback",tags=["insGen"])
async def post_description(body:Feedback):
    print("This is a user feedback :",body.__str__())
    # Assuming you want to use the feedback in some way
    try:
        result = Continue_Auto_InsightGen(body.feedback, body.thread_id)
        feedback = await anext(result)  # Use anext() instead of __anext__()
        # print("RESULT", feedback)
    except Exception as e:
        print(f"Error in post_description: {str(e)}")
        raise
    return {"feedback": feedback}
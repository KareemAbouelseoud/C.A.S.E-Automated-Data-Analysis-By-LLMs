import asyncio
from config import *
insGen_router = APIRouter(prefix="/insGen", tags=["insGen"])
insGen_service = insGenService()
@insGen_router.get("/project/{project_id}/description")

async def get_description(project_id):
    if not project_id:
        raise HTTPException(status_code=400, detail="Project ID cannot be empty")
    try:
        task = asyncio.create_task(insGen_service.get_description(project_id))
        result = await task 
        return result
    except Exception as e:
        print(f"Error in get_description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@insGen_router.post("/description/feedback")
async def post_description(body:Feedback):
    return await insGen_service.accept_human_feedback(body)
@insGen_router.post("/project/{project_id}/save_Insights")
async def post_save_Insights(body:SaveInsights, project_id:str):
    if not project_id:
        raise HTTPException(status_code=400, detail="Project ID cannot be empty")
    asyncio.create_task(insGen_service.save_Insights(body, project_id))
    pass

@insGen_router.get("/custom_events")
async def custom_events():
    #TODO: Actually implement this function to return real-time updates
    # All we need is to create a container for the events and then use the event stream to send updates to the client
    # For now, we will just simulate some updates
    async def event_stream():
        static_updates = [
            {"message": "First update"},
            {"message": "Second update"},
            {"message": "Third update"},
            {"message": "Final update"}
        ]
        for update in static_updates:
            await asyncio.sleep(1)  # Small delay to simulate processing
            yield f"event: update\ndata: {json.dumps(update)}\n\n"
        yield "event: done\ndata: {}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
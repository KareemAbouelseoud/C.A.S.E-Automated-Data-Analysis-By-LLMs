import asyncio
from config import *
insGen_router = APIRouter(prefix="/insGen", tags=["insGen"])
insGen_service = insGenService()
@insGen_router.get("/description")

async def get_description():
    return await insGen_service.get_description()

@insGen_router.post("/description/feedback")
async def post_description(body:Feedback):
    return await insGen_service.accept_human_feedback(body)

@insGen_router.get("/custom_events")
async def custom_events():
    async def event_stream():
        for i in range(5):
            await asyncio.sleep(2)
            yield f"event: update\ndata: {json.dumps({'message': f'Update {i+1}'})}\n\n"
        yield "event: done\ndata: {}\n\n"  # Custom event when completed
    return StreamingResponse(event_stream(), media_type="text/event-stream")
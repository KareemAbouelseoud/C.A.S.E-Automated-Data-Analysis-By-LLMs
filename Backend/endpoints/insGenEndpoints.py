
from config import *
insGen_router = APIRouter()
insGen_service = insGenService()
@insGen_router.get("/InsGen/description")

async def get_description():
    return await insGen_service.get_description()

@insGen_router.post("/InsGen/description/feedback")
async def post_description(body:Feedback):
    return await insGen_service.accept_human_feedback(body)
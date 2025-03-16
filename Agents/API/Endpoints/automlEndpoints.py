from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from AutoML import pipeline
from .dataItems import Train
autoML_router = APIRouter()

@autoML_router.post("/autoML/train", tags=["AutoML"])
async def predict(item: Train):
    return StreamingResponse(pipeline.automl(
        project_id=item.project_id,
        data_report=item.data_report,
        label=item.target_feature,
        features=item.training_features,
        user_preferences=item.user_input if item.user_input else None,
        mode=item.mode),
        media_type="text/event-stream")
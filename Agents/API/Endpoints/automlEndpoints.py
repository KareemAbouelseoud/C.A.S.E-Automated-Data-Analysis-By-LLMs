from fastapi import APIRouter
from fastapi.responses import StreamingResponse,JSONResponse
from AutoML import pipeline
from AutoML.Inference.predict import predict
from .dataItems import Train, PredictRequest
import asyncio
from cachetools import TTLCache
from API.Requests import projectRequests

# Cache: Stores models with a TTL (time-to-live)
MODEL_TTL_SECONDS = 600  # Cache expires after 10 minutes
MAX_CACHE_SIZE = 10  # Store up to 10 models

model_cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=MODEL_TTL_SECONDS)
preprocessing_cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=MODEL_TTL_SECONDS)

autoML_router = APIRouter()

@autoML_router.post("/autoML/train", tags=["AutoML"])
async def train(item: Train):
    return StreamingResponse(pipeline.automl(
        project_id=item.project_id,
        data_report=item.data_report,
        label=item.target_feature,
        features=item.training_features,
        user_preferences=item.user_input if item.user_input else None,
        mode=item.mode),
        media_type="text/event-stream")

# Prediction route
@autoML_router.post("/autoML/predict", tags=['AutoML'])
async def predict_endpoint(req: PredictRequest):
    model_id = req.model_id
    parts = model_id.split("_", 1)  # Split at the first underscore
    project_id = parts[0]
    model_name = parts[1] if len(parts) > 1 else ""
    if model_id in model_cache and project_id+'_X' in preprocessing_cache:
        print("Cache hit",flush=True)
        model = model_cache[model_id]
        Xpreprocessing_pipeline = preprocessing_cache[project_id+'_X']
        
        cached = True
    else:
        # Load from backend and cache them
        # Split model_id into project_id and model_name

        
        # Load model using the split components
        model = await projectRequests.get_model(project_id,model_name)
        model_cache[model_id] = model

        Xpreprocessing_pipeline = await projectRequests.get_preprocessing_pipeline(project_id, 'X')
        preprocessing_cache[project_id+'_X'] = Xpreprocessing_pipeline

        cached = False

    # Predict
    predictions=await predict(data=req.data, model=model, Xpreprocessing_pipeline=Xpreprocessing_pipeline,feature_columns=req.feature_columns if req.feature_columns else None)
    
    return JSONResponse(content={'predictions': predictions, 'cached': cached})

# Periodic cache cleanup task
async def cache_cleanup():
    while True:
        await asyncio.sleep(MODEL_TTL_SECONDS)  # Wait for TTL before clearing
        model_cache.clear()
        preprocessing_cache.clear()


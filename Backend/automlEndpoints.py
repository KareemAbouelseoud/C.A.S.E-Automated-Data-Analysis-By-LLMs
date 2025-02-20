import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter
from Agents.AutoML import pipeline
from dataItems import Train
automl_router = APIRouter()


@automl_router.get('/train/{project_id}')
async def train(project_id:str,item: Train):
    return {'data':pipeline.automl(project_id,item.mode,item.target_feature,item.training_features,item.user_input)}
    
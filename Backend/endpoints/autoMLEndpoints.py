from fastapi import APIRouter
from fastapi import HTTPException
from dataItems import Train

autoML=APIRouter()

@autoML.get('/project/{project_id}/AutoML/train/',tags=["Project"])
async def train(project_id:str,item: Train):
    pass

    
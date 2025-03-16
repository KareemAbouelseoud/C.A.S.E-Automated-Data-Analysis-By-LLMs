from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from dataItems import Train
import requests
from services.project_service import ProjectService
project_service = ProjectService()

autoML_router=APIRouter()
url="http://Agents:8006"

@autoML_router.post('/project/{project_id}/AutoML/train/',tags=["Project"])
async def train(project_id:str,item: Train):
    data = item.model_dump()
    data['project_id'] = project_id
    data_report=await project_service.fetch_data_report(project_id)
    data['data_report'] = data_report
    response = requests.post(url + "/autoML/train", json=data, stream=True)
    return StreamingResponse(response.iter_content(chunk_size=4096), media_type="text/event-stream")
    
from fastapi import APIRouter , UploadFile, File, Form,HTTPException
from fastapi.responses import StreamingResponse
from dataItems import Train
import requests
from services.project_service import ProjectService
import io
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

@autoML_router.post('/project/{project_id}/AutoML/save-model', tags=["Project"])
async def save_model(
    project_id: str, 
    model_name: str,
    model_file: UploadFile = File(...)
):
    """
    Upload and save a model file for a specific project
    
    - **project_id**: ID of the project to save the model for
    - **model_file**: The model file to upload (binary)
    - **model_name**: Name of the model
    """
    try:
        # Read the uploaded file content
        contents = await model_file.read()
        
        # Save the model using project service
        result = await project_service.save_model(project_id, contents, model_name)
        
        return {
            "message": "Model saved successfully", 
            "result": result,
            "filename": model_file.filename,
            "model_name": model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save model: {str(e)}")

@autoML_router.post('/project/{project_id}/AutoML/save-model-report', tags=["Project"])
async def save_model_report(
            project_id: str,
            report:str,
        ):
            """
            Upload and save a model report for a specific project
            
            - **project_id**: ID of the project to save the report for
            - **report**: The model report to upload"""
            try:                
                # Save the model report using project service
                result = await project_service.save_model_report(project_id, report)
                if result:
                    return {
                        "message": "Model report saved successfully", 
                        "result": result,
                    }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save model report: {str(e)}")

@autoML_router.post('/project/{project_id}/AutoML/save-preprocessing-pipeline/{pipeline_type}', tags=["Project"])
async def save_preprocessing_pipeline(
    project_id: str,
    pipeline_type: str,
    pipeline_file: UploadFile = File(...),
):
    """
    Upload and save a preprocessing pipeline for a specific project
    
    - **project_id**: ID of the project to save the pipeline for
    - **pipeline_file**: The preprocessing pipeline file to upload
    - **pipeline_type**: Type of pipeline ('X' or 'Y')
    """
    try:
        # Validate pipeline type
        if pipeline_type not in ['X', 'Y']:
            raise HTTPException(status_code=400, detail="Pipeline type must be either 'X' or 'Y'")
            
        # Read the uploaded file content
        contents = await pipeline_file.read()
        
        # Save the preprocessing pipeline using project service
        result = await project_service.save_preprocessing_pipeline(
            project_id, 
            pipeline_type,
            contents
        )
        if result:
            return {
                "message": f"{pipeline_type} preprocessing pipeline saved successfully", 
                "result": result,
                "filename": pipeline_file.filename,
                "pipeline_type": pipeline_type
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save preprocessing pipeline: {str(e)}")
    

@autoML_router.get('/project/{project_id}/AutoML/model', tags=["Project"])
async def get_model(project_id: str, model_name: str):
    try:
        # Fetch model data as raw bytes
        model_data = await project_service.fetch_model(project_id, model_name)
        if not model_data:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found for project '{project_id}'")

        # Stream model without saving to disk
        buffer = io.BytesIO(model_data)
        return StreamingResponse(buffer, media_type="application/octet-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model: {str(e)}")
    
@autoML_router.get('/project/{project_id}/AutoML/model-report', tags=["Project"])
async def get_model_report(project_id: str):
    try:
        # Fetch model report data as raw bytes
        model_report = await project_service.fetch_model_report(project_id)

        if not model_report:
            raise HTTPException(status_code=404, detail=f"Model report not found for project '{project_id}'")

        return {"model_report": model_report}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model report: {str(e)}")

@autoML_router.get('/project/{project_id}/AutoML/preprocessing-pipeline/{pipeline_type}', tags=["Project"])
async def get_preprocessing_pipeline(project_id: str, pipeline_type: str):
    try:
        # Fetch preprocessing pipeline data as raw bytes
        pipeline_data = await project_service.fetch_pipeline(project_id, pipeline_type)
        if not pipeline_data:
            raise HTTPException(status_code=404, detail=f"Preprocessing pipeline '{pipeline_type}' not found for project '{project_id}'")
    except:
        raise HTTPException(status_code=404, detail=f"Preprocessing pipeline '{pipeline_type}' not found for project '{project_id}'")
    try:
        # Stream pipeline without saving to disk
        buffer = io.BytesIO(pipeline_data)
        return StreamingResponse(buffer, media_type="application/octet-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve preprocessing pipeline: {str(e)}")
    
@autoML_router.delete('/project/{project_id}/AutoML/delete-all', tags=["Project"])
async def delete_all_automl_data(project_id: str):
    """
    Delete all AutoML data for a specific project
    
    - **project_id**: ID of the project whose AutoML data should be deleted
    """
    try:
        # Delete model, model report, and preprocessing pipelines
        result = await project_service.delete_automl_data(project_id)
        
        return {
            "message": "All AutoML data deleted successfully",
            "project_id": project_id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete AutoML data: {str(e)}")
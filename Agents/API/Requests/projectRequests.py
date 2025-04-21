import httpx
import pandas as pd
from io import StringIO
from joblib import Memory
import joblib
import json
import io
import requests
from ..Endpoints.dataItems import SaveInsights
url="http://Backend:8005"

# Create a memory cache in a temporary directory
memory = Memory(location='./.cache', verbose=0)

# Apply caching to the requests function
@memory.cache
async def get_dataset(project_id):
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url + f"/project/{project_id}/fetchDataset")
            except Exception as e:
                print("Error in fetching dataset from backend:", e)
                response = await client.get(f"http://localhost:8005/project/{project_id}/fetchDataset")
        dataset = json.loads(response.json()["data"])
    except Exception as e:
        print(f"Error fetching dataset: {e}")
        raise e
        return None
    return pd.DataFrame(dataset)


@memory.cache
async def get_data_report(project_id):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url + f"/project/{project_id}/fetchDataReport")
    except:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8005/project/{project_id}/fetchDataReport")
    
    return response.json()['data']
async def save_insights(project_id, insights:SaveInsights):
    """
    Uploads insights to the backend API.
    
    Args:
        project_id (str): The ID of the project
        insights (dict): The insights data to upload
        
    Returns:
        dict: Response from the server or None if an error occurred
    """
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url + f"/insGen/project/{project_id}/save_Insights",
                    json= insights.model_dump(mode='json'),timeout=100
                )
            except Exception as e:
                print("Error in posting insights:", e)
                response = await client.post(
                    f"http://localhost:8005/insGen/project/{project_id}/save_Insights",
                    json=insights.model_dump(mode='json'),timeout=100
                )
        
        if response.status_code == 200:
            print("Insights uploaded successfully.")
            return response.json()
        else:
            print(f"Failed to upload insights: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
                
    except Exception as e:
        print(f"Error uploading insights: {e}")
        return None
async def get_preprocessing_pipeline(project_id, pipeline_type):
    """
    Retrieves a preprocessing pipeline from the backend API.
    
    Args:
        project_id (str): The ID of the project
        pipeline_type (str): Type of the pipeline ('X' or 'Y')
        
    Returns:
        The deserialized pipeline object or None if not found/error occurred
    """
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url + f"/project/{project_id}/AutoML/preprocessing-pipeline/{pipeline_type}"
                )
            except:
                response = await client.get(
                    f"http://localhost:8005/project/{project_id}/AutoML/preprocessing-pipeline/{pipeline_type}"
                )
        
        if response.status_code == 200:
            pipeline_bytes = io.BytesIO(response.content)
            return joblib.load(pipeline_bytes)
        else:
            print(f"Failed to fetch pipeline: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error retrieving preprocessing pipeline: {e}")
        return None

async def send_preprocessing_pipeline(project_id, pipeline_type, pipeline_data):
    """
    Uploads a preprocessing pipeline to the backend API efficiently using in-memory file.
    
    Args:
        project_id (str): The ID of the project
        pipeline_type (str): Type of the pipeline ('X' or 'Y')
        pipeline_data: The pipeline object to upload
        
    Returns:
        dict: Response from the server or None if an error occurred
    """
    try:
        buffer = io.BytesIO()
        joblib.dump(pipeline_data, buffer)
        buffer.seek(0)
        
        files = {'pipeline_file': ('pipeline.pkl', buffer, 'application/octet-stream')}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url + f"/project/{project_id}/AutoML/save-preprocessing-pipeline/{pipeline_type}",
                    files=files
                )
            except:
                response = await client.post(
                    f"http://localhost:8005/project/{project_id}/AutoML/save-preprocessing-pipeline/{pipeline_type}",
                    files=files
                )
            
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to upload pipeline: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
                
    except Exception as e:
        print(f"Error uploading preprocessing pipeline: {e}")
        return None

async def get_model(project_id, model_name):
    """
    Retrieves a model from the backend API.
    
    Args:
        project_id (str): The ID of the project
        model_name (str): Name of the model to retrieve
        
    Returns:
        The deserialized model object or None if not found/error occurred
    """
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url + f"/project/{project_id}/AutoML/model",
                    params={'model_name': model_name}
                )
            except:
                response = await client.get(
                    f"http://localhost:8005/project/{project_id}/AutoML/model",
                    params={'model_name': model_name},
                )
        
        if response.status_code == 200:
            model_bytes = io.BytesIO(response.content)
            return joblib.load(model_bytes)
        else:
            print(f"Failed to fetch model: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error retrieving model: {e}")
        return None

async def save_model(project_id, model_name, model_data):
    """
    Uploads a model to the backend API using an in-memory file.
    
    Args:
        project_id (str): The ID of the project
        model_name (str): Name of the model to save
        model_data: The model object to upload
        
    Returns:
        dict: Response from the server or None if an error occurred
    """
    try:
        buffer = io.BytesIO()
        joblib.dump(model_data, buffer)
        buffer.seek(0)
        
        files = {'model_file': (f'{model_name}.pkl', buffer, 'application/octet-stream')}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url + f"/project/{project_id}/AutoML/save-model",
                    files=files,
                    params={'model_name': model_name}
                )
            except:
                response = client.post(
                    f"http://localhost:8005/project/{project_id}/AutoML/save-model",
                    files=files,
                    params={'model_name': model_name}
                )
            
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to upload model: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
                
    except Exception as e:
        print(f"Error uploading model: {e}")
        return None

async def save_model_report(project_id, report):
    """
    Uploads a model report to the backend API.
    
    Args:
        project_id (str): The ID of the project
        report (dict or str): The model report to upload. If dict, it will be converted to str
        
    Returns:
        dict: Response from the server or None if an error occurred
    """
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url + f"/project/{project_id}/AutoML/save-model-report",
                    json={'report': report}
                )
            except Exception as e:
                raise e
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to upload model report: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
                
    except Exception as e:
        print(f"Error uploading model report: {e}")
        return None

async def delete_all_automl_data(project_id):
    """
    Deletes all AutoML data for a specific project from the backend API.
    
    Args:
        project_id (str): The ID of the project
        
    Returns:
        dict: Response from the server or None if an error occurred
    """
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    url + f"/project/{project_id}/AutoML/delete-all"
                )
            except:
                response = await client.delete(
                    f"http://localhost:8005/project/{project_id}/AutoML/delete-all"
                )
            
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to delete AutoML data: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
                
    except Exception as e:
        print(f"Error deleting AutoML data: {e}")
        return None

async def get_model_report(project_id):
    """
    Retrieves the model report from the backend API.
    
    Args:
        project_id (str): The ID of the project
        """
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url + f"/project/{project_id}/AutoML/model-report"
                )
            except:
                response = await client.get(
                    f"http://localhost:8005/project/{project_id}/AutoML/model-report"
                )
        
        if response.status_code == 200:
            return json.loads(response.json()['model_report'])['report']
        else:
            print(f"Failed to fetch model report: HTTP {response.status_code}",flush=True)
            print(f"Response: {response.text}",flush=True)
            return None
                
    except Exception as e:
        print(f"Error retrieving model report: {e}")
        return None
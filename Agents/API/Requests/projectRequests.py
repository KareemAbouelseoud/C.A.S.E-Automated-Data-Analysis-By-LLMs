import requests
import pandas as pd
from io import StringIO
from joblib import Memory
import os
import joblib
import json
import io
url="http://Backend:8005"

# Create a memory cache in a temporary directory
memory = Memory(location='./.cache', verbose=0)

# Apply caching to the requests function
@memory.cache
async def get_dataset(project_id):
    try:
        try:
            response = requests.get(url + f"/project/{project_id}/fetchDataset")
        except:
            response = requests.get(f"http://localhost:8005/project/{project_id}/fetchDataset")
        dataset=response.json()['data']
    except:
        return None
    return pd.read_json(StringIO(dataset))


@memory.cache
async def get_data_report(project_id):
    try:
        response = requests.get(url + f"/project/{project_id}/fetchDataReport")
    except:
        response = requests.get(f"http://localhost:8005/project/{project_id}/fetchDataReport")
    
    return response.json()['data']

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
        # First try with Docker network URL
        try:
            response = requests.get(
                url + f"/project/{project_id}/AutoML/preprocessing-pipeline/{pipeline_type}"
            )
        except:
            # Fallback to localhost
            response = requests.get(
                f"http://localhost:8005/project/{project_id}/AutoML/preprocessing-pipeline/{pipeline_type}"
            )
        
        if response.status_code == 200:
            # The requests library automatically handles the streaming for us
            # and collects all the chunks into response.content
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
        # Create in-memory file-like object
        buffer = io.BytesIO()
        joblib.dump(pipeline_data, buffer)
        buffer.seek(0)  # Go back to the beginning of the buffer
        
        # Create files dict with the in-memory file object
        files = {'pipeline_file': ('pipeline.pkl', buffer, 'application/octet-stream')}
        
        # First try with Docker network URL
        try:
            response = requests.post(
                url + f"/project/{project_id}/AutoML/save-preprocessing-pipeline/{pipeline_type}",
                files=files
            )
        except:
            # Fallback to localhost
            response = requests.post(
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
        # First try with Docker network URL
        try:
            response = requests.get(
                url + f"/project/{project_id}/AutoML/model",
                params={'model_name': model_name}
            )
        except:
            # Fallback to localhost
            response = requests.get(
                f"http://localhost:8005/project/{project_id}/AutoML/model",
                params={'model_name': model_name},
            )
        
        if response.status_code == 200:
            # The requests library automatically handles the streaming for us
            # and collects all the chunks into response.content
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
        # Create in-memory file-like object instead of writing to disk
        buffer = io.BytesIO()
        joblib.dump(model_data, buffer)
        buffer.seek(0)  # Go back to the beginning of the buffer
        
        # Create files dict with the in-memory file object
        files = {'model_file': (f'{model_name}.pkl', buffer, 'application/octet-stream')}
        
        # First try with Docker network URL
        try:
            response = requests.post(
                url + f"/project/{project_id}/AutoML/save-model",
                files=files,
                params={'model_name': model_name}
            )
        except:
            # Fallback to localhost
            response = requests.post(
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
        # Convert dict to string if needed
        if isinstance(report, dict):
            report_str = json.dumps(report)
        else:
            report_str = str(report)
        
        # First try with Docker network URL
        try:
            response = requests.post(
                url + f"/project/{project_id}/AutoML/save-model-report",
                # Send the report directly as the request body
                params={'report': report_str}
            )
        except:
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
        # First try with Docker network URL
        try:
            response = requests.delete(
                url + f"/project/{project_id}/AutoML/delete-all"
            )
        except:
            # Fallback to localhost
            response = requests.delete(
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
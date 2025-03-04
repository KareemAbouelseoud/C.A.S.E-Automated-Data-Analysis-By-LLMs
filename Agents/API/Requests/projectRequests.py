import requests
import pandas as pd
from io import StringIO
from joblib import Memory
import os
import joblib
url="http://Backend:8005"

# Create a memory cache in a temporary directory
memory = Memory(location='./.cache', verbose=0)

# Apply caching to the requests function
@memory.cache
async def get_dataset(project_id):
    try:
        response = requests.get(url + f"/project/{project_id}/fetchDataset")
    except:
        response = requests.get(f"http://localhost:8005/project/{project_id}/fetchDataset")
    dataset=response.json()['data']
    return pd.read_json(StringIO(dataset))

def get_X_pipeline(project_id):
    pipeline_path = f"./static/{project_id}_X_pipeline.pkl"
    if os.path.exists(pipeline_path):
        return joblib.load(pipeline_path)
    else:
        return None

def save_X_pipeline(project_id, pipeline_data):
    pipeline_path = f"./static/{project_id}_X_pipeline.pkl"
    os.makedirs(os.path.dirname(pipeline_path), exist_ok=True)
    joblib.dump(pipeline_data, pipeline_path)

def get_Y_pipeline(project_id):
    pipeline_path = f"./static/{project_id}_Y_pipeline.pkl"
    if os.path.exists(pipeline_path):
        return joblib.load(pipeline_path)
    else:
        return None

def save_Y_pipeline(project_id, pipeline_data):
    pipeline_path = f"./static/{project_id}_Y_pipeline.pkl"
    os.makedirs(os.path.dirname(pipeline_path), exist_ok=True)
    joblib.dump(pipeline_data, pipeline_path)

def get_model(project_id, model_name):
    model_path = f"./static/{project_id}_{model_name}_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        return None

def save_model(project_id, model_name, model_data):
    model_path = f"./static/{project_id}_{model_name}_model.pkl"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model_data, model_path)



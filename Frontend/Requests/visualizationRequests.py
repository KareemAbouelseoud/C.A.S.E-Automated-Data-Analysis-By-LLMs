import sys
import os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
import json
from dataModels.visualization import ChatViz
import pandas as pd
url='http://Backend:8005'

def fetch_visualizations(project_id:str):
    response = requests.get(url+f'/project/{project_id}/visualization/get_Auto_Gen')
    return json.loads(response.json())['visualizations']

def fetch_chat_visualizations(project_id:str):
    response = requests.get(url+f'/project/{project_id}/visualization/get_Chat_Viz')
    return json.loads(response.json())['visualizations']


def save_chat_visualizations(project_id:str,new_viz:ChatViz):    
    response = requests.post(url+f'/project/{project_id}/visualization/Chat_viz',json=new_viz.model_dump())
    return response.status_code==200

def make_serializable(obj):
    """
    Convert an object to a serializable format.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Interval):
        return {'left': obj.left, 'right': obj.right, 'closed': obj.closed}
    
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj
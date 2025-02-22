import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
import json
from dataModels.visualization import ChatViz


def fetch_visualizations(project_id:str):
    url = f'http://127.0.0.1:8000/project/{project_id}/visualization/get_Auto_Gen'
    response = requests.get(url)
    return json.loads(response.json())['visualizations']

def fetch_chat_visualizations(project_id:str):
    url = f'http://127.0.0.1:8000/project/{project_id}/visualization/get_Chat_Viz'
    response = requests.get(url)
    return json.loads(response.json())['visualizations']


def save_chat_visualizations(project_id:str,new_viz:ChatViz):
    url = f'http://127.0.0.1:8000/project/{project_id}/visualization/Chat_viz'
    response = requests.post(url,json=new_viz.model_dump())
    return response.status_code==200
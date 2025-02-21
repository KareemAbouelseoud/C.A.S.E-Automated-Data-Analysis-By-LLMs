import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
import json


def train(project_id,target_feature,training_features,mode,user_input=None):
    url = f'http://127.0.0.1:8000/project/{project_id}/AutoML/train/'
    response = requests.post(url,json={'project_id':project_id,
                                       'target_feature':target_feature,
                                       'training_features':training_features,
                                       'mode':mode,
                                       'user_input':user_input})
    
    return response.json()['data']
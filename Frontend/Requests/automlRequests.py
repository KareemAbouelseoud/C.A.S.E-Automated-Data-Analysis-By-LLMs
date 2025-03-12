import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
import json
url="http://Backend:8005"


def train(project_id,target_feature,training_features,mode,user_input=None):
    response = requests.post(url+f'/project/{project_id}/AutoML/train/',
                             json={ 'target_feature':target_feature,
                                       'training_features':training_features,
                                       'mode':mode,
                                       'user_input':user_input})
    
    return response.json()['data']
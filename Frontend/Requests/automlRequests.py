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
                                       'user_input':user_input},stream=True)
    
    return response

def predict(project_id, model_name, data,feature_columns):
    print("Predicting",data)
    data_payload = {'model_name': model_name, 'data': data}
    if feature_columns is not None:
        data_payload['feature_columns'] = feature_columns
    
    response = requests.post(url + f'/project/{project_id}/AutoML/predict/',
                            json=data_payload)
    
    if response.status_code == 200:
        return (response.json()['predictions'])
    else:
        print(f"Failed to predict: HTTP {response.status_code}")
        print(f"Response: {response.text}",flush=True)
        return None
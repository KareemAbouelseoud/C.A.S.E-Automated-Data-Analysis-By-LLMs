import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import numpy as np
from AutoML.Supervisor.pipeline import graph
from API.Requests import projectRequests
import asyncio
import fireducks.pandas as pd
CONFIGURATIONS= {
    'recursion_limit': 100,
}
def make_serializable(obj):
    """
    Convert an object to a serializable format.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(make_serializable(i) for i in obj)
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
    elif isinstance(obj, pd.Index):
        return obj.tolist()
    else:
        return obj
    
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Index):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

async def automl(project_id,data_report,mode,label,features=None,user_preferences=None):
    print("Removing Project Pipelines and Models",flush=True)
    # Create and gather tasks for concurrent execution
    await asyncio.gather(
        asyncio.create_task(projectRequests.delete_all_automl_data(project_id))
    )
    print("AUTOML STARTED")
    async for chunk in graph.astream({'data_report':data_report,'project_id':project_id,'mode':mode,'X_columns':features,'y_column':label,'user_preferences':user_preferences,'steps':0},config=CONFIGURATIONS, stream_mode=['updates','values']):
        if chunk[0] == 'values':
            response=chunk[1]
        elif chunk[0] == 'updates':
            for node,update in chunk[1].items():
                yield node
    
    models = {k: v for k, v in response['models'].items() if v.get('completed') is True}
    
    # Remove and save X/Y preprocessing pipelines and model objects from each model dict
    for model_name, model_dict in models.items():
        # Extract and remove the pipelines and model object if present
        x_pipeline = model_dict.pop('X_pipeline', None)
        y_pipeline = model_dict.pop('Y_pipeline', None)
        model_obj = model_dict.pop('model', None)
        if x_pipeline:
            asyncio.create_task(projectRequests.send_preprocessing_pipeline(project_id, model_name,'X', x_pipeline))
        if y_pipeline:
            asyncio.create_task(projectRequests.send_preprocessing_pipeline(project_id, model_name,'Y', y_pipeline))
        if model_obj:
            asyncio.create_task(projectRequests.save_model(project_id, model_name, model_obj))
        # Update the models dictionary with the modified model_dict
        models[model_name] = model_dict
            
    final_response = {
        'mode':response['mode'],
        'user_preferences':response['user_preferences'],
        'X_columns':response['X_columns'],
        'y_column':response['y_column'],
        'problem_type':response['problem_type'],
        'models':models,
    }
    final_response = make_serializable(final_response) 
    asyncio.create_task(projectRequests.save_model_report(project_id, final_response))
    yield json.dumps(final_response, cls=NumpyEncoder)

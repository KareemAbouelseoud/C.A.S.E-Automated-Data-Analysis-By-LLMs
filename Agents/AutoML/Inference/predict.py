import asyncio
import fireducks.pandas as pd
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','modelTraining')))
from trainer import preprocess_without_cross_validation
import numpy as np

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
    else:
        return obj
    
async def predict(data, model, Xpreprocessing_pipeline,feature_columns):
    """
    Predicts the target variable using the model and preprocessing pipeline.
    
    Args:
        data (List[dict]): List of dict for prediction
        model (object): The model object
        Xpreprocessing_pipeline (object): The preprocessing pipeline for X
        Ypreprocessing_pipeline (object): The preprocessing pipeline for Y
        
    Returns:
        List[float]: List of predictions
    """
    data = pd.DataFrame(data)
    data['row_id'] = range(len(data))
    try:
        # Preprocess asynchronously
        data, _, _, processor = await asyncio.to_thread(
            preprocess_without_cross_validation, 
            data=data, 
            preprocessor=Xpreprocessing_pipeline, 
            fit=False
        )
        if feature_columns:
            data = data[feature_columns]
        predictions = await asyncio.to_thread(model.predict, data)
        print(predictions,flush=True)
        return make_serializable(predictions)
    except Exception as e:
       return None
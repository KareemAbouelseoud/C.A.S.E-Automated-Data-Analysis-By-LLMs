from API.Requests import projectRequests
from typing import Literal
from sklearn import model_selection
import pandas as pd
from sklearn.metrics import accuracy_score,precision_score, recall_score, f1_score, roc_auc_score,confusion_matrix,precision_recall_curve,roc_curve
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','modelTraining')))
from trainer import preprocess_without_cross_validation,merge_data
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
    
async def evaluator_node(state):
    """
    Check code

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """
    print("---Evaluating ALL Models---")
    #region Processing Test
    project_id = state["project_id"]
    completed_models = []
    for model in state["models"]:
        if 'completed' in model:
            completed_models.append(model)
    
    df= await projectRequests.get_dataset(project_id)
    X=df[state['X_columns']]
    y=df[state['y_column']]
    stratify = state['stratify'] if 'stratify' in state else False
    _,X_test, _, y_test=model_selection.train_test_split(X,y,test_size=state['test_size'],shuffle=state['shuffle'],stratify=y if stratify else None,random_state=42)
    
    Xpreprocessing_pipeline=projectRequests.get_X_pipeline(project_id)
    Ypreprocessing_pipeline=projectRequests.get_Y_pipeline(project_id)

    X_test['row_id'] = range(len(X_test))
    y_test = pd.DataFrame({state['y_column']: y_test, 'row_id': range(len(y_test))})
    
    if Xpreprocessing_pipeline:
        X_temp_test,_,_,_=preprocess_without_cross_validation(X_test,Xpreprocessing_pipeline,fit=False)
    else:
        X_temp_test=X_test

    if Ypreprocessing_pipeline:
        y_temp_test,_,_,_=preprocess_without_cross_validation(y_test,Ypreprocessing_pipeline,fit=False)
    else:
        y_temp_test=y_test

    try:
        X_test,y_test=merge_data(X_temp_test,y_temp_test,state['y_column'])
    except:
        # If merging fails, try to adjust the dataframes by dropping the row_id columns
        # which were only added for merging purposes
        X_test = X_temp_test
        y_test = y_temp_test[state['y_column']]  # Keep only the target column
    
    # Exclude object columns that might cause issues during prediction
    X_test = X_test.select_dtypes(exclude=['object'])
    
    #endregion
    #region Evaluating
    reports=[]
    for model_dict in completed_models:

        model_name=model_dict['model']
        model=projectRequests.get_model(project_id,model_name)

        if state['problem_type']=='classification':
            metrics=classification_metrics(model,X_test,y_test)
        else:
            metrics=regression_metrics(model,X_test,y_test)

        report={
            "model":model_name,
            'problem_type':state['problem_type'],
            "metrics":metrics
        }
        reports.append(report)
    reports=make_serializable(reports)
    
    projectRequests.save_model_report(project_id,reports)
    return {"evaluation_reports":json.dumps(reports)}
    
    #endregion

def classification_metrics(model,X_test,y_true):
    print(X_test)
    y_pred=model.predict(X_test)
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')
    
    try:
        y_probs = model.predict_proba(X_test)[:, 1]  # Extract probabilities of the positive class
    except:
        y_probs = model.decision_function(X_test)
    
    # Compute ROC-AUC score
    if y_true.nunique() > 2:
        roc_auc = roc_auc_score(y_true, y_probs, multi_class='ovr')
    else:
        roc_auc = roc_auc_score(y_true, y_probs)
    
    cm = confusion_matrix(y_true, y_pred)

    # Compute precision-recall curve
    precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_probs)

    # Compute ROC curve
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    
    # Return metrics
    metrics={
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
        "precision_recall_curve": (precision_curve, recall_curve),
        "roc_curve": (fpr, tpr)
    }
    return metrics


def regression_metrics(y_true,y_pred):
    pass 
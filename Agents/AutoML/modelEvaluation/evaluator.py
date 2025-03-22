from API.Requests import projectRequests
from typing import Literal
from sklearn import model_selection
import pandas as pd
from sklearn.metrics import accuracy_score,precision_score, recall_score, f1_score, roc_auc_score,confusion_matrix,precision_recall_curve,roc_curve
from sklearn.inspection import permutation_importance
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','modelTraining')))
from trainer import preprocess_without_cross_validation,merge_data,get_cached_pipeline,fetch_model
import numpy as np
import asyncio
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

    # Run async operations concurrently
    Xpreprocessing_pipeline, Ypreprocessing_pipeline, df = await asyncio.gather(
        get_cached_pipeline(project_id, 'X'),
        get_cached_pipeline(project_id, 'Y'),
        projectRequests.get_dataset(project_id)
    )
    X=df[state['X_columns']]
    y=df[state['y_column']]
    stratify = state['stratify'] if 'stratify' in state else False
    _,X_test, _, y_test=model_selection.train_test_split(X,y,test_size=state['test_size'],shuffle=state['shuffle'],stratify=y if stratify else None,random_state=42)
    

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

    X_test,y_test=merge_data(X_temp_test,y_temp_test,state['y_column'])
    
    # Exclude object columns that might cause issues during prediction
    X_test = X_test.select_dtypes(exclude=['object'])
    


    #endregion
    #region Evaluating
    reports=[]
    for model_dict in completed_models:

        model_name=model_dict['model']
        X_test_copy=X_test[model_dict['X_columns'] if 'X_columns' in model_dict else X_test.columns]
        model=await fetch_model(project_id,model_name)

        if state['problem_type']=='classification':
            metrics=classification_metrics(model,X_test_copy,y_test,state['y_column'])
        else:
            metrics=regression_metrics(model,X_test_copy,y_test)

        report={
            "model":model_name,
            'problem_type':state['problem_type'],
            "metrics":metrics,
            'test_count':X_test.shape[0]
        }
        reports.append(report)
    reports=make_serializable(reports)
    
    # Create an async task to save the model report without waiting for it to complete
    asyncio.create_task(projectRequests.save_model_report(project_id, reports))
    return {"evaluation_reports":json.dumps(reports)}
    
    #endregion

def classification_metrics(model,X_test,y_true,y_column):
    y_pred=model.predict(X_test)
    print(y_pred,flush=True)
    print(y_true,flush=True)

    # If y_true is a 2D array, select the first column
    if len(y_true.shape) > 1 and y_true.shape[1] > 1:
        y_true = y_true[y_column]
    
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
        "precision_recall_curve": [precision_curve, recall_curve],
        "roc_curve": [fpr, tpr],
    }
    feat_importance=get_feature_importance(model,X_test,y_true,feature_names=X_test.columns.tolist())
    if feat_importance:
        metrics['feature_importance']=make_serializable(feat_importance)
        
    return metrics

def regression_metrics(y_true,y_pred):
    pass 

def get_feature_importance(model, X, y=None, feature_names=None, n_repeats=10, random_state=42):
    """
    Returns feature importance for a given model.
    
    Parameters:
        model : estimator or pipeline
            The trained model (or a pipeline) to extract feature importance from.
        X : array-like or DataFrame
            The input features used to train the model.
        y : array-like, optional
            The target variable. Required for permutation importance if the model
            does not have a built-in feature importance attribute.
        feature_names : list, optional
            Names of the features. If X is a DataFrame, these will be used by default.
        n_repeats : int, default=10
            Number of times to permute a feature for permutation importance.
        random_state : int, default=42
            Random state for permutation importance.
    
    Returns:
        importance_dict : dict
            A dictionary mapping feature names to their importance scores.
    """
    
    # If X is a DataFrame and feature_names not provided, get columns names
    if feature_names is None:
        if isinstance(X, pd.DataFrame):
            feature_names = X.columns.tolist()
        else:
            feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    
    # Handle the case where model is a pipeline by extracting the final estimator
    if hasattr(model, 'steps'):
        # You might want to adjust this if your pipeline does additional processing
        model = model.steps[-1][1]
    
    # Check for built-in feature_importances_ attribute (e.g., tree-based models)
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    
    # Check for coef_ attribute (e.g., linear models)
    elif hasattr(model, "coef_"):
        coef = model.coef_
        # If multi-class (2D array), we take the mean of absolute values across classes
        if coef.ndim > 1:
            importances = np.mean(np.abs(coef), axis=0)
        else:
            importances = np.abs(coef)
    
    # Fall back on permutation importance if y is provided
    elif y is not None:
        result = permutation_importance(model, X, y, n_repeats=n_repeats, random_state=random_state)
        importances = result.importances_mean
    else:
        return None
    
    # Create a dictionary mapping feature names to importance scores
    importance_dict = dict(zip(feature_names, importances))
    return importance_dict
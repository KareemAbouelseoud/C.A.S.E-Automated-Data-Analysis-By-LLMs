import sys
import os
from typing_extensions import TypedDict,NotRequired
from langgraph.graph import StateGraph, START
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AutoML.Splitting.splitter import splitter_node
from AutoML.Preprocessing.pipeline import graph as preprocessor_graph
from AutoML.ModelSelection.selector import model_selector_node,brancher as model_selector_brancher
from AutoML.modelTraining.trainer import trainer_node, decide_to_finish as trainer_decide_to_finish
from AutoML.modelEvaluation.evaluator import evaluator_node
from AutoML.HPO.tuner import tuner_node,tuner_decide_to_finish
from AutoML.Explanation.explainer import explainer_node
import json
from AutoML.Preprocessing.preprocessingTools import remove_project_pipelines,remove_project_models
from API.Requests import projectRequests

CONFIGURATIONS= {
    'recursion_limit': 100,
}
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    data_report: NotRequired[str] # Data Report
    mode: str # Mode Selected by the User
    user_preferences: NotRequired[str] # User Preferences
    
    #Data Names
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)
    problem_type: NotRequired[str] # Problem Type Identified by the LLM

    #Splitting
    splitting_logic: NotRequired[str] # Splitting Steps Documented for the User and rest of Agents
    test_size: NotRequired[float] # Test Size
    test_count: NotRequired[int] # Test Count
    shuffle: NotRequired[bool] # Shuffle
    stratify: NotRequired[bool] # Stratify
    cross_validation: NotRequired[bool] # Cross Validation
    
    n_splits: NotRequired[int] # Number of Splits
    val_size: NotRequired[float] # Validation Size
    val_count: NotRequired[int] # Validation Count

    train_count: NotRequired[int] # Train Count
    
    #Tuning
    n_iter: NotRequired[int] # Number of Iterations
    params_distribution: NotRequired[dict] # Parameters Distribution

    #Preprocessing Pipeline
    X_preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    Y_preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents

    X_pipeline_html: NotRequired[str] # X Pipeline HTML
    Y_pipeline_html: NotRequired[str] # Y Pipeline HTML
    
    #Model
    models: NotRequired[list] # Model Names Selected by LLM
    models_completed: NotRequired[int] # Number of Models Completed

    #Evaluation
    evaluation_reports: NotRequired[list] # Evaluation Reports


builder = StateGraph(State)
builder.add_node('splitter_node', splitter_node)
builder.add_node('preprocessor_node', preprocessor_graph)
builder.add_node("model_selector_node", model_selector_node)
builder.add_node("model_trainer_node",trainer_node)
builder.add_node("model_tuner_node",tuner_node)
builder.add_node("model_evaluator_node",evaluator_node)

builder.add_edge(START, 'splitter_node')
builder.add_edge('splitter_node', 'preprocessor_node')
builder.add_edge('preprocessor_node', "model_selector_node")
builder.add_conditional_edges('model_selector_node',model_selector_brancher)
builder.add_conditional_edges("model_tuner_node", tuner_decide_to_finish)
builder.add_conditional_edges('model_trainer_node',trainer_decide_to_finish)

graph = builder.compile()




async def automl(project_id,data_report,mode,label,features=None,user_preferences=None):
    print("Removing Project Pipelines and Models",flush=True)
    await remove_project_pipelines(project_id)
    await remove_project_models(project_id)
    await projectRequests.delete_all_automl_data(project_id)
    print("AUTOML STARTED")
    async for chunk in graph.astream({'data_report':data_report,'project_id':project_id,'mode':mode,'X_columns':features,'y_column':label,'user_preferences':user_preferences},config=CONFIGURATIONS, stream_mode=['updates','values']):
        if chunk[0] == 'values':
            response=chunk[1]
        elif chunk[0] == 'updates':
            for node,update in chunk[1].items():
                yield node
    
    models = [i for i in response['models'] if 'completed' in i]
    final_response = {
        'mode':response['mode'],
        'user_preferences':response['user_preferences'],
        'X_columns':response['X_columns'],
        'y_column':response['y_column'],
        'problem_type':response['problem_type'],
        'splitting_logic':response['splitting_logic'],
        'X_preprocessing_logic':await explainer_node(response['X_preprocessing_logic'].content) if 'X_preprocessing_logic' in response and response['X_preprocessing_logic'] else None,
        'Y_preprocessing_logic':await explainer_node(response['Y_preprocessing_logic'].content) if 'Y_preprocessing_logic' in response and response['Y_preprocessing_logic'] else None,
        'test_size':(response['test_size'],),
        'shuffle':response['shuffle'],
        'stratify':response['stratify'],
        'cross_validation':response['cross_validation'],
        'n_splits':response['n_splits'] if 'n_splits' in response else None,
        'val_size':response['val_size'] if  'val_size' in response else None,
        'n_iter':response['n_iter'] if 'n_iter' in response else None,
        'models':models,
        'evaluation_reports':response['evaluation_reports'] ,
        'X_pipeline_html':response['X_pipeline_html'] if 'X_pipeline_html' in response else None,
        'Y_pipeline_html':response['Y_pipeline_html'] if 'Y_pipeline_html' in response else None,
        'test_count':response['test_count'] if 'test_count' in response else None,
        'val_count':response['val_count'] if 'val_count' in response else None,
        'train_count':response['train_count'] if 'train_count' in response else None,
    }
    yield json.dumps(final_response)

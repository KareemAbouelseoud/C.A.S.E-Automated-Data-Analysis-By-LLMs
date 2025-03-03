import sys
import os
from typing_extensions import TypedDict,NotRequired
from langgraph.graph import StateGraph, START
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AutoML.Splitting.splitter import splitter_node
from AutoML.Preprocessing.pipeline import graph as preprocessor_graph
from AutoML.ModelSelection.selector import model_selector_node
from AutoML.modelTraining.pipeline import model_trainer_node
from AutoML.modelEvaluation.pipeline import model_evaluator_node


class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    data_report: NotRequired[str] # Data Report
    dataframe: NotRequired[object] # Dataframe
    mode: str # Mode Selected by the User
    user_preferences: NotRequired[str] # User Preferences
    #Data Names
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)
    problem_type: NotRequired[str] # Problem Type Identified by the LLM

    #Splitting
    splitting_logic: NotRequired[str] # Splitting Steps Documented for the User and rest of Agents
    X_train: NotRequired[object] # Training Features
    X_test: NotRequired[object] # Testing Features
    y_train: NotRequired[object] # Training Target
    y_test: NotRequired[object] # Testing Target

    #Preprocessing Pipeline
    X_preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    Y_preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    
    #Model
    training_logic: NotRequired[str] # Training Steps Documented for the User and rest of Agents
    models: NotRequired[list] # Model Names Selected by LLM




builder = StateGraph(State)
builder.add_node('splitter_node', splitter_node)
builder.add_node('preprocessor_node', preprocessor_graph)
builder.add_node("model_selector_node", model_selector_node)
builder.add_node("model_trainer_node",model_trainer_node)
builder.add_node("model_evaluator_node",model_evaluator_node)

builder.add_edge(START, 'splitter_node')
builder.add_edge('splitter_node', 'preprocessor_node')
builder.add_edge('preprocessor_node', "model_selector_node")
builder.add_edge("model_selector_node", "model_trainer_node")
builder.add_edge("model_trainer_node","model_evaluator_node")
graph = builder.compile()




async def automl(project_id,data_report,dataframe,mode,label,features=None,user_preferences=None):
    print("AUTOML STARTED")
    async for chunk in graph.astream({'project_id':project_id,'mode':mode,'X_columns':features,'y_column':label,'user_preferences':user_preferences}, stream_mode=['updates','values']):
        if chunk[0] == 'values':
            response=chunk[1]
        elif chunk[0] == 'updates':
            print("Update:",chunk[1])

    print("Final Response:",response)
import asyncio
asyncio.run(automl('1','Athena','Survived'))
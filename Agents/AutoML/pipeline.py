import sys
import os
from typing_extensions import TypedDict,Annotated,NotRequired
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage
import operator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AutoML.Splitting.splitter import splitter_node
from AutoML.Preprocessing.pipeline import graph as preprocessor_graph
from sklearn.compose import ColumnTransformer


class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    mode: str # Mode Selected by the User
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
    preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    
    #Model
    models: NotRequired[list[str]] # Model Names Selected by LLM
    model_objects: NotRequired[list[object]] # Model Objects




builder = StateGraph(State)
builder.add_node('splitter_node', splitter_node)
builder.add_node('preprocessor_node', preprocessor_graph)
builder.add_edge(START, 'splitter_node')
builder.add_edge('splitter_node', 'preprocessor_node')
graph = builder.compile()




async def automl(project_id,mode,label,features=None):
    print("AUTOML STARTED")
    response=await graph.ainvoke({'project_id':project_id,'mode':mode,'X_columns':features,'y_column':label})
    # This will contain everything needed. from steps taken by each agent to the final model(s) and their performance
    print("Finished")
import asyncio
asyncio.run(automl('1','Athena','Survived'))
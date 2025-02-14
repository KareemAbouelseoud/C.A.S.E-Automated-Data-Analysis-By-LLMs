import sys
import os
from typing_extensions import TypedDict,Annotated,NotRequired
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage
import operator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from AutoML.Splitting.splitter import splitter_node
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    mode: str # Mode Selected by the User
    pipeline: object # Preprocessing Pipeline
    data_report: NotRequired[str] # Data Report
    #Data Names
    columns: NotRequired[list[str]] # Columns Names
    X_columns: NotRequired[list[str]] # X Columns
    y_column: NotRequired[str] # Y Column
    #Actual Data
    X_train: NotRequired[object] # Training Features
    X_test: NotRequired[object] # Testing Features
    y_train: NotRequired[object] # Training Target
    y_test: NotRequired[object] # Testing Target




builder = StateGraph(State)
builder.add_node('splitter_node', splitter_node)
builder.add_edge(START, 'splitter_node')

graph = builder.compile()
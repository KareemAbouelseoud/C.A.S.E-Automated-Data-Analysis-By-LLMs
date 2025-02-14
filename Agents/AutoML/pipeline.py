import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing_extensions import TypedDict,Annotated,NotRequired
import operator
from langgraph.graph import StateGraph, START, END
from Agents.codeGeneration.caller import caller_node
from Agents.codeGeneration.planner import planner_node,planner_brancher,tool_brancher
from Agents.codeGeneration.mainTools import tool_node
from Agents.codeGeneration.designer import designer_chain
from Agents.codeGeneration.coder.coderPipeline import coder
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage
import operator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Database import mainDatabase

class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    mode: str # Mode Selected by the User
    pipeline: object # Preprocessing Pipeline
    target_feature: str # Target Feature name
    data_report: NotRequired[str] # Data Report
    columns: NotRequired[list[str]] # Columns Names




builder = StateGraph(State)

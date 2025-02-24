import operator
from langchain_core.messages import AnyMessage
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict,Annotated,NotRequired
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from preprocessingTools import tool_node
from planner import planner_node
from Agents.AutoML.Preprocessing.caller import caller_node,should_continue

load_dotenv()
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    data_report: NotRequired[str] # Data Report
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)
    preprocessing_messages: Annotated[list[AnyMessage], operator.add]
    preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents

builder = StateGraph(State)

builder.add_node("caller_node", caller_node) 
builder.add_node("planner_node", planner_node) 
builder.add_node("tools",tool_node)

builder.add_edge(START, "planner_node")
builder.add_edge("planner_node", "caller_node")
builder.add_conditional_edges("caller_node", should_continue)
builder.add_edge('tools','caller_node')
graph = builder.compile()
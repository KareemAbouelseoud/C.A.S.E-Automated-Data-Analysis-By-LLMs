import operator
from langchain_core.messages import AnyMessage
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict,Annotated,NotRequired
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from preprocessingTools import tool_node
from preprocessor import preprocessor_node,should_continue
    
load_dotenv()
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)
    preprocessing_messages: Annotated[list[AnyMessage], operator.add]

builder = StateGraph(State)

builder.add_node("preprocessor_node", preprocessor_node) 
builder.add_node("tools",tool_node)

builder.add_edge(START, "preprocessor_node")
builder.add_edge("preprocessor_node", "tools")
builder.add_conditional_edges('tools', should_continue)
graph = builder.compile()
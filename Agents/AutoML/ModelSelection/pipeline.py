import operator
from langchain_core.messages import AnyMessage
from langgraph.graph import START, StateGraph
from typing import TypedDict, Annotated, NotRequired
from dotenv import load_dotenv
import os
import sys
import asyncio
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Database import mainDatabase
from selector import selector_node,should_continue  # Update with actual import path

load_dotenv()

class GraphState(TypedDict):
    """
    Represents the state of the model selection workflow using basic dict types
    """
    project_id: str
    mode: str
    X_columns: NotRequired[list[str]]
    y_column: NotRequired[str]
    problem_type: str
    
    preprocessing_logic: NotRequired[str]
    models: NotRequired[list]


# Create workflow builder
builder = StateGraph(GraphState)

# Add nodes
builder.add_node("model_selector", selector_node)

# Set up edges
builder.add_edge(START, "model_selector")
builder.add_conditional_edges("model_selector", should_continue)

# Compile the graph
model_selection_graph = builder.compile()
"""
callerpipeline.py

This module sets up a state graph for the caller component of the preprocessing module.
It defines the workflow for calling tools to process preprocessing tasks.

Dependencies:
- typing_extensions
- operator
- langgraph.graph
- langchain_core.messages
- pandas
"""
from io import StringIO
from typing_extensions import TypedDict, Annotated, NotRequired, Literal
import operator
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage
import pandas as pd
from .caller import caller_node
from .mainTools import tool_node, tool_brancher
from typing import  Tuple, TypedDict
from typing_extensions import Any

class CallerState(TypedDict):
    """
    A class to represent the state of the caller pipeline.
    
    Attributes:
        project_id: The ID of the project
        messages: List of messages in the conversation
        preprocessing_tasks: The task to process
        target_column: The column to process
        strategy: The strategy to use
        dataframe: Input DataFrame
        preprocessed_dataframe: Processed DataFrame
        generated_errors: List of code solutions that failed validation
        executed_responses: List of successfully executed code solutions
    """
    project_id: str
    messages: Annotated[list[AnyMessage], operator.add]
    preprocessing_tasks: str  # The task to process
    target_column: str  # The column to process
    strategy: str  # The strategy to use
    dataframe: NotRequired[Any]
    preprocessed_dataframe: NotRequired[Any]

def check_dframe(state) :
    """
    Check if the DataFrame is valid.

    Args:
        state (dict): The current graph state

    Returns:
        bool: True if DataFrame is valid, False otherwise
    """
    df = state.get('dataframe')
    if not isinstance(df, pd.DataFrame):    
        return {"dataframe":pd.read_json(StringIO(state['dataframe']))}
    return{"dataframe": df}

# Create state graph
workflow = StateGraph(CallerState)

# Add nodes
workflow.add_node("check_dframe", check_dframe)  # Check if DataFrame is valid
workflow.add_node("caller", caller_node)  # Call tools
workflow.add_node("tools", tool_node)  # Execute tools


# Build graph
workflow.add_edge(START, "check_dframe")
workflow.add_edge("check_dframe", "caller")
workflow.add_edge("caller", "tools")
workflow.add_conditional_edges("tools", tool_brancher)


caller_pipeline = workflow.compile(checkpointer=False)

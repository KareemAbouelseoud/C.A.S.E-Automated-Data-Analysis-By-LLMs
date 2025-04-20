"""
pipeline.py

This module sets up a state graph for the preprocessing module, defining the nodes and edges for the workflow.
It integrates various components such as the caller, coder, planner, and tools to create a complete preprocessing pipeline.

Dependencies:
- typing_extensions
- operator
- langgraph.graph
- caller
- planner
- mainTools
- langchain_core.messages
- coder
- os
- sys
"""
from caller import caller_node
from planner import planner_node
from mainTools import tool_node, tool_brancher
from coder.coderPipeline import coder_pipeline
from langchain_core.messages import AnyMessage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from API.Requests.projectRequests import get_dataset
from typing_extensions import TypedDict, Annotated, NotRequired
import operator
from langgraph.graph import StateGraph, START
import pandas as pd

class State(TypedDict):
    """
    A class to represent the state of the preprocessing module.
    """
    project_id: str
    data_report: NotRequired[str]
    next : NotRequired[str]
    messages: Annotated[list[AnyMessage], operator.add]
    preprocessing_task: NotRequired[str]
    target_column: NotRequired[str]
    strategy: NotRequired[str]
    preprocessed_dataframe: NotRequired[pd.DataFrame]
    generation: NotRequired[dict]
    iterations: NotRequired[int] = 0
    error: NotRequired[str]

# Create state graph
builder = StateGraph(State)

# Add nodes
builder.add_node("planner", planner_node)
builder.add_node("caller", caller_node)
builder.add_node("coder", coder_pipeline)
builder.add_node("tools", tool_node)

# Add edges
builder.add_edge(START, "planner")
builder.add_edge("planner", "caller")
builder.add_edge("planner", "coder")
builder.add_edge("caller", "tools")
builder.add_conditional_edges("tools", tool_brancher)

# Compile graph
preprocessing_pipeline = builder.compile()

async def preprocess_data(project_id: str, preprocessed_dataframe: pd.DataFrame, preprocessing_task: str, target_column: str,strategy: str = None):
    """
    Execute the preprocessing pipeline on the data.
    
    Args:
        project_id: The ID of the project
        preprocessing_task: The preprocessing task to perform
        target_column: The target column to preprocess
        strategy: The strategy to use for the preprocessing task

    Returns:
        The preprocessed data and visualization metadata
    """
    response = await preprocessing_pipeline.ainvoke({
        "project_id": project_id,
        "messages": [],
        "preprocessing_task": preprocessing_task,
        "target_column": target_column,
        "strategy": strategy,
        "preprocessed_dataframe": preprocessed_dataframe
    })
    
    return response

if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        project_id = "1234567890"
        preprocessing_task = "handle_missing_values"
        target_column = "age"
        strategy = "mean"
        dataframe = get_dataset(project_id)
        try:
            result = await preprocess_data(project_id, dataframe, preprocessing_task, target_column,strategy)
            print("Preprocessing completed successfully")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error during preprocessing: {str(e)}")
            sys.exit(1)

    asyncio.run(main())

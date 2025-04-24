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
from planner import planner_node, planner_brancher
from mainTools import tool_node, tool_brancher
from coder.coderPipeline import coder_pipeline
from langchain_core.messages import AnyMessage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
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
    preprocessing_tasks: NotRequired[list[dict]]  # List of tasks, each with task, column, and strategy
    current_task_index: NotRequired[int]  # Index of current task being processed
    dataframe: NotRequired[pd.DataFrame]
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
builder.add_conditional_edges("planner", planner_brancher, {"caller": "caller", "coder": "coder"})
builder.add_edge("caller", "tools")
builder.add_conditional_edges("tools", tool_brancher)

# Compile graph
preprocessing_pipeline = builder.compile()

async def preprocess_data(project_id: str, dataframe: pd.DataFrame, preprocessing_tasks: list[dict]):
    """
    Execute the preprocessing pipeline on the data with multiple tasks.
    
    Args:
        project_id: The ID of the project
        dataframe: The input DataFrame
        preprocessing_tasks: List of dictionaries containing:
            - task: The preprocessing task to perform
            - column: The target column to preprocess
            - strategy: The strategy to use for the preprocessing task

    Returns:
        The preprocessed data and visualization metadata
    """
    response = await preprocessing_pipeline.ainvoke({
        "project_id": project_id,
        "messages": [],
        "preprocessing_tasks": preprocessing_tasks,
        "current_task_index": 0,
        "dataframe": dataframe
    })
    
    return response

if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        project_id = "1"
        preprocessing_tasks = [
            {
                "task": "handle_missing_values",
                "column": "Age",
                "strategy": "mean"
            },
            {
                "task": "remove_outliers",
                "column": "Fare",
                "strategy": "zscore"
            }
        ]
        dataframe = pd.read_csv(r"C:\Users\mshir\OneDrive\Desktop\Private\Python_projects\Graduation Project\datasets\titanic\Titanic-Dataset.csv")
        try:
            result = await preprocess_data(project_id, dataframe, preprocessing_tasks)
            print(f"Result: {result['preprocessed_dataframe']}")
        except Exception as e:
            print(f"Error during preprocessing: {str(e)}")
            sys.exit(1)

    asyncio.run(main())


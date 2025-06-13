"""
pipeline.py

This module sets up a state graph for the preprocessing module, defining the nodes and edges for the workflow.
It integrates various components such as the caller, coder, planner, and tools to create a complete preprocessing pipeline.
"""

from .planner import planner_node
from .coder.coderPipeline import coder_pipeline
from .caller.callerPipeline import caller_pipeline
from langchain_core.messages import AnyMessage
import sys
import os
from io import StringIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from typing_extensions import TypedDict, Annotated, NotRequired, List
import operator
from langgraph.graph import StateGraph, START
import pandas as pd
import asyncio

class State(TypedDict):
    project_id: str
    messages: Annotated[list[AnyMessage], operator.add]
    recommendation: List[object]
    preprocessing_tasks:List[object]
    dataframe: NotRequired[str]
    preprocessed_dataframe: NotRequired[str]
    error: NotRequired[str]
    executed_responses: NotRequired[list[dict]]

async def preprocess_data(project_id: str, dataframe, recommendation):
    """
    Execute the preprocessing pipeline on the data using steps from the recommender.
    
    Args:
        project_id: The ID of the project.
        dataframe: Input as a DataFrame or JSON string.
        recommendation: A single dict or a list of dicts from the recommendation engine.

    Returns:
        dict: {
            "preprocessed_dataframe": JSON string of processed DataFrame,
            "messages": list,
            "executed_responses": list
        }
    """

    if isinstance(recommendation, dict):
        recommendation = [recommendation]

    preprocessing_tasks = []
    for item in recommendation:
        steps = item.get("args", {}).get("preprocessing_steps", [])
        for step in steps:
            if not all(k in step for k in ("preprocessing_step", "column_name")):
                print(f"[WARNING] Skipping malformed step: {step}")
                continue
            preprocessing_tasks.append({
                "task": step["preprocessing_step"],
                "column": step["column_name"],
                "strategy": step["explanation"] if "explanation" in step else " "
            })

    #initial state
    initial_state = {
        "project_id": project_id,
        "messages": [],
        "preprocessing_tasks": preprocessing_tasks,
        "dataframe": dataframe,
        "error": '',
        "executed_responses": []
    }


    coder_tasks, caller_tasks = await planner_node(initial_state)

    #convert stringified DataFrame to pd DataFrame
    if isinstance(dataframe, str):
        try:
            current_df = pd.read_json(StringIO(dataframe), orient='columns')
        except Exception as e:
            raise ValueError(f"Failed to parse input DataFrame JSON string: {e}")
    elif isinstance(dataframe, pd.DataFrame):
        current_df = dataframe.copy()
    else:
        raise TypeError("Invalid input: dataframe must be a pd.DataFrame or JSON string")

  
    for task in caller_tasks:
        caller_result = await caller_pipeline.ainvoke({
            "project_id": project_id,
            "messages": initial_state["messages"],
            "dataframe": current_df,
            "preprocessing_tasks": task["task"],
            "target_column": task["column"],
            "strategy": task["strategy"],
            "executed_responses": initial_state["executed_responses"]
        })
        if "preprocessed_dataframe" in caller_result and isinstance(caller_result["preprocessed_dataframe"], pd.DataFrame):
            current_df = caller_result["preprocessed_dataframe"]

   
    for task in coder_tasks:
        coder_result = await coder_pipeline.ainvoke({
            "project_id": project_id,
            "messages": initial_state["messages"],
            "dataframe": current_df,
            "preprocessing_tasks": task["task"],
            "target_column": task["column"],
            "strategy": task["strategy"],
            "executed_responses": initial_state["executed_responses"]
        })
        if "preprocessed_dataframe" in coder_result and isinstance(coder_result["preprocessed_dataframe"], pd.DataFrame):
            current_df = coder_result["preprocessed_dataframe"]

    #convert to json if pd df
    if isinstance(current_df, pd.DataFrame):
        preprocessed_json = current_df.to_json(orient="records")
    else:
        raise TypeError("Final output is not a valid DataFrame.")

    result = {
        "preprocessed_dataframe": preprocessed_json,
        "messages": initial_state["messages"],
        "executed_responses": initial_state["executed_responses"]
    }

    return result

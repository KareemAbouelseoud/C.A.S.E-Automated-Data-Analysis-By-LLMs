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
from .planner import planner_node
from .coder.coderPipeline import coder_pipeline
from .caller.callerPipeline import caller_pipeline
from langchain_core.messages import AnyMessage
import sys
import os
from io import StringIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from typing_extensions import TypedDict, Annotated, NotRequired,List
import operator
from langgraph.graph import StateGraph, START
import pandas as pd
import asyncio

class State(TypedDict):
    """
    A class to represent the state of the preprocessing module.
    
    Attributes:
        project_id: The ID of the project
        messages: List of messages in the conversation
        preprocessing_tasks: List of preprocessing tasks to perform
        dataframe: Input DataFrame
        preprocessed_dataframe: Processed DataFrame
        error: Error status
        executed_responses: List of successfully executed code solutions
    """
    project_id: str
    messages: Annotated[list[AnyMessage], operator.add]
    recommendation: List[object]  
    dataframe: NotRequired[str]
    preprocessed_dataframe: NotRequired[str]
    error: NotRequired[str] = ''
    executed_responses: NotRequired[list[dict]] = [] 

async def preprocess_data(project_id: str, dataframe, recommendation):
    """
    Execute the preprocessing pipeline on the data using steps from the recommender.

    Args:
        project_id: The ID of the project
        dataframe: The input DataFrame
        recommendation: Either a single dict or a list of dicts from the recommendation engine.

    Returns:
        dict: Contains:
            - preprocessed_dataframe: The processed DataFrame
            - messages: List of messages from the process
            - executed_responses: List of successfully executed code solutions
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
                "strategy": step.get("explanation", "")
            })

    initial_state = {
        "project_id": project_id,
        "messages": [],
        "recommendation": preprocessing_tasks,
        "preprocessing_tasks": preprocessing_tasks,
        "dataframe": dataframe,
        "error": '',
        "executed_responses": []
    }

    coder_tasks, caller_tasks = await planner_node(initial_state)

    if isinstance(dataframe, str):
        current_df = pd.read_json(StringIO(dataframe), orient='columns')
    else:
        current_df = dataframe.copy()

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
        if "preprocessed_dataframe" in caller_result:
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
        if "preprocessed_dataframe" in coder_result:
            current_df = coder_result["preprocessed_dataframe"]

    result = {
        "preprocessed_dataframe": current_df.to_json(orient="records"),
        "messages": initial_state["messages"],
        "executed_responses": initial_state["executed_responses"]
    }

    if isinstance(result.get( "preprocessed_dataframe"), pd.DataFrame):
        result[ "preprocessed_dataframe"] = result["preprocessed_dataframe"].to_json(orient="records")

    return result

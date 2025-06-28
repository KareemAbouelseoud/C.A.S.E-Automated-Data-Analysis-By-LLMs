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
from typing_extensions import Any

class State(TypedDict):
    project_id: str
    messages: Annotated[list[AnyMessage], operator.add]
    recommendation: List[object]
    preprocessing_tasks:List[object]
    dataframe: NotRequired[Any]
    preprocessed_dataframe: NotRequired[Any]
    error: NotRequired[str]
    executed_responses: NotRequired[list[dict]]


import json

async def preprocess_data(project_id: str, dataframe, recommendation):
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
        dict: Contains:
            - preprocessed_dataframe: The processed DataFrame
            - messages: List of messages from the process
            - executed_responses: List of successfully executed code solutions
    """
    if isinstance(dataframe, str):
        parsed = json.loads(dataframe)
        dataframe=pd.DataFrame(parsed)
        
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
   #Change
    # preprocessing_tasks = []

    # for item in recommendation:
    #     steps = item.get("args", {}).get("preprocessing_steps", [])
    #     if steps:
    #         step = steps[0]  # take only the first one
    #         if all(k in step for k in ("preprocessing_step", "column_name")):
    #             preprocessing_tasks.append({
    #                 "task": step["preprocessing_step"],
    #                 "column": step["column_name"],
    #                 "strategy": step.get("explanation", " ")
    #             })
    #         else:
    #             print(f"[WARNING] Skipping malformed first step: {step}")
    #     break  


    #initial state
    initial_state = {
        "project_id": project_id,
        "messages": [],
        "preprocessing_tasks": preprocessing_tasks,
        "dataframe": dataframe,
        "error": '',
        "executed_responses": []
    }

    
    # Run pipeline to get task routing
    coder_tasks, caller_tasks = await planner_node(initial_state)
    
    # Process caller tasks with state tracking
    current_df = initial_state["dataframe"].copy()
    for task in caller_tasks:
        caller_result = await caller_pipeline.ainvoke({
            "project_id": project_id,
            "messages": initial_state["messages"],
            "dataframe": current_df,  # Use the current state of the DataFrame
            "preprocessing_tasks": task["task"],
            "target_column": task["column"],
            "strategy": task["strategy"],
            "executed_responses": initial_state["executed_responses"]
        })
        if "preprocessed_dataframe" in caller_result:
            current_df = caller_result["preprocessed_dataframe"]
    
    # Process coder tasks with state tracking
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
    # if coder_tasks:
    #     task = coder_tasks[0]
    #     coder_result = await coder_pipeline.ainvoke({
    #         "project_id": project_id,
    #         "messages": initial_state["messages"],
    #         "dataframe": current_df,  
    #         "preprocessing_tasks": task["task"],
    #         "target_column": task["column"],
    #         "strategy": task["strategy"],
    #         "executed_responses": initial_state["executed_responses"]
    #     })
    #     if "preprocessed_dataframe" in coder_result:
    #         current_df = coder_result["preprocessed_dataframe"]

    
    # Return the final state of the DataFrame
    return {
        "preprocessed_dataframe": current_df,
        "messages": initial_state["messages"],
        "executed_responses": initial_state["executed_responses"]
    }
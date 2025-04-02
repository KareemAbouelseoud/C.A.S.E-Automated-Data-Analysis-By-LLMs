"""
pipeline.py

This module sets up a state graph for the application, defining the nodes and edges for the workflow.
It integrates various components such as the caller,coder, planner, tools, and designer to create a complete pipeline.

Dependencies:
- typing_extensions
- operator
- langgraph.graph
- caller
- planner
- mainTools
- designer
- langchain_core.messages
- coder
- os
- sys

Usage:
1. Ensure that the required dependencies are installed.
2. Set up the necessary environment variables in a .env file.
3. Use the generate_visualizations function to generate visualizations based on the project ID.

Classes:
- State: A TypedDict class to represent the state of the application.

Functions:
- generate_visualizations: Generates visualizations based on the project ID.

Variables:
- builder: An instance of StateGraph to build the state graph.
- graph: The compiled state graph.
"""
import sys

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from typing_extensions import TypedDict,Annotated,NotRequired
import operator
from langgraph.graph import StateGraph,START
from .caller import caller_node
from .planner import planner_node
from .mainTools import tool_node,tool_brancher
from .designer import designer_node
from .coder.coderPipeline import coder_pipeline
from langchain_core.messages import AnyMessage
import operator
import asyncio
import time

class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id: str
    messages: Annotated[list[AnyMessage], operator.add]
    visualization: NotRequired[Annotated[list[dict], operator.add]]
    next: NotRequired[str]
    data_report: NotRequired[str]
    iterations: NotRequired[int] = 0



builder = StateGraph(State)
builder.add_node("caller", caller_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, 'caller')
builder.add_edge('caller','tools')
builder.add_conditional_edges('tools',tool_brancher)

caller_pipeline = builder.compile()
    
async def generate_visualizations(data_report, project_id, features=None):
    start_time = time.time()  # Start measuring time
    while True:
        response = await designer_node(data_report, features)
        if response:
            break
    caller_list, code_list = await planner_node(response)
    
    # Create tasks for caller visualizations
    caller_tasks = [
        caller_pipeline.ainvoke({
            'project_id': project_id,
            'messages': [{"role": "human", "content": f"Here is the design needed: {str(design)}, and here is the data report crucial for the naming convention: {data_report}"}]
        }) 
        for design in caller_list
    ]
    
    # Create tasks for coder visualizations
    coder_tasks = [
        coder_pipeline.ainvoke({
            'project_id': project_id,
            'messages': [{"role": "human", "content": f"Here is the design needed: {str(design)}"}],
            'data_report': data_report
        })
        for design in code_list
    ]
    
    # Run all tasks concurrently
    all_results = await asyncio.gather(*caller_tasks, *coder_tasks, return_exceptions=True)

    # Process all results in one loop
    visualizations = []
    for result in all_results:
        if isinstance(result, Exception):
            # Log the exception and continue
            print(f"Task failed with exception: {result}")
        else:
            # Collect successful results
            if 'visualization' in result and result['visualization']:
                visualizations.append(result['visualization'])

    end_time = time.time()  # End measuring time
    print(f"Time taken for generate_visualizations: {end_time - start_time:.2f} seconds")

    return visualizations

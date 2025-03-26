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
from langgraph.graph import StateGraph, START, END
from .caller import caller_node
from .planner import planner_node,planner_brancher,tool_brancher
from .mainTools import tool_node
from .designer import designer_node
from .coder.coderPipeline import coder
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage
import operator

class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id: str
    messages: Annotated[list[AnyMessage], operator.add]
    visualization: NotRequired[Annotated[list[dict], operator.add]]
    next: NotRequired[str]
    data_report: NotRequired[str]



builder = StateGraph(State)
builder.add_node("planner", planner_node)
builder.add_node("caller", caller_node)
builder.add_node("tools", tool_node)
builder.add_node("coder", coder)

builder.add_edge(START, "planner")
builder.add_conditional_edges("planner", planner_brancher)
builder.add_edge('caller','tools')
builder.add_conditional_edges('tools',tool_brancher)
builder.add_edge('coder',END)

viz_graph = builder.compile()
    
async def generate_visualizations(data_report,project_id,features=None):
    while True:
        response= await designer_node(data_report,features)
        if response:
            break

    visualizations=[]
    for idx,design in  enumerate(response):
        try:
            graph_response= await viz_graph.ainvoke({'data_report':str(data_report),'messages':[{"role":"human","content":str(design)}],'project_id':project_id})
            print("Graph response",graph_response)
            if 'visualization' in graph_response and graph_response['visualization']:
                visualizations.append(graph_response['visualization'])    
        except Exception as e:
            print(f"Error in graph response for design {idx}: {design}")
            print(e)
            continue
    return visualizations     
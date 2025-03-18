"""
preprocessing_pipeline.py

This module defines the main workflow for data preprocessing operations, 
orchestrating between predefined tools and code generation when needed.
"""
import os
import sys
from typing_extensions import TypedDict, Annotated, NotRequired
from typing import Literal, Sequence, Dict, Any
import operator
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Agents.preprocessingModule.planner import planner_node, planner_brancher
from Agents.preprocessingModule.caller import caller_node, tool_brancher
from Agents.preprocessingModule.preprocessingtools import tool_node
from Agents.preprocessingModule.coder.pipeline import coder_workflow
from .parallelStepsEnabler import dependency_analyzer, execute_parallel_steps


class PreprocessingState(TypedDict):
    """State representation for preprocessing pipeline"""
    project_id: str
    current_step: Dict[str, Any]
    preprocessing_steps: Sequence[Dict[str, Any]]
    dataset_state: Dict[str, Any]
    messages: Annotated[list[AnyMessage], operator.add]
    logs: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
    transformers: Dict[str, Any]
    next: NotRequired[Literal["caller", "coder", "__end__"]]
    parallel_steps: NotRequired[Dict[str, Dict]]
    processing_mode: Literal["sequential", "parallel"]

builder = StateGraph(PreprocessingState)

builder.add_node("planner", planner_node)
builder.add_node("caller", caller_node)
builder.add_node("tools", tool_node)
builder.add_node("coder", coder_workflow)
builder.add_node("parallel_orchestrator", execute_parallel_steps)


builder.add_edge(START, "planner")
builder.add_conditional_edges(
    "planner",
    lambda state: "parallel_orchestrator" if should_parallelize(state) else planner_brancher,
    {
        "parallel_orchestrator": "parallel_orchestrator",
        "caller": "caller",
        "coder": "coder"
    }
)

builder.add_edge("parallel_orchestrator", "planner")
builder.add_edge("caller", "tools")
builder.add_conditional_edges(
    "tools",
    tool_brancher,
    {
        "__end__": END,
        "planner": "planner"
    }
)
builder.add_edge("coder", END)

preprocessing_pipeline = builder.compile()

def should_parallelize(state: PreprocessingState) -> bool:
    independent, _ = dependency_analyzer(state["preprocessing_steps"])
    return len(independent) > 1 and state.get("processing_mode", "parallel") == "parallel"

async def generate_preprocessing(project_id: str, steps: Sequence[Dict[str, Any]]) -> Dict:
    """
    Execute preprocessing pipeline for a project
    
    Args:
        project_id: Unique project identifier
        steps: List of preprocessing steps to apply
        
    Returns:
        Dict containing final state and processing results
    """
    initial_state = {
        "project_id": project_id,
        "preprocessing_steps": steps,
        "current_step": {},
        "dataset_state": {},
        "messages": [],
        "logs": [],
        "errors": [],
        "transformers": {}
    }
    
    try:
        result = await preprocessing_pipeline.ainvoke(initial_state)
        return {
            "status": "success",
            "project_id": project_id,
            "transformers": result["transformers"],
            "logs": result["logs"],
            "errors": result["errors"],
            "dataset_snapshot": result["dataset_state"]
        }
    except Exception as e:
        return {
            "status": "error",
            "project_id": project_id,
            "error": str(e),
            "logs": initial_state["logs"],
            "errors": initial_state["errors"]
        }
"""
preprocessing_pipeline.py

This module defines the main workflow for data preprocessing operations, 
orchestrating between predefined tools and code generation when needed.
"""
import os
import sys
import asyncio
from typing_extensions import TypedDict, Annotated, NotRequired
from typing import Literal, Sequence, Dict, List, Any
import operator
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Agents.preprocessingModule.planner import planner_node, planner_brancher
from Agents.preprocessingModule.caller import caller_node, tool_brancher
from Agents.preprocessingModule.preprocessingtools import tool_node
from Agents.preprocessingModule.coder.pipeline import coder_workflow
from .parallelStepsEnabler import dependency_analyzer, execute_parallel_steps
import pandas as pd


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
    
data = {
    "Survived": [0, 1, 1, 1, 0, 0],
    "Pclass": [3, 1, 3, 1, 3, 3],
    "Name": [
        "Braund, Mr. Owen Harris",
        "Cumings, Mrs. John Bradley (Florence Briggs Thayer)",
        "Heikkinen, Miss. Laina",
        "Futrelle, Mrs. Jacques Heath (Lily May Peel)",
        "Allen, Mr. William Henry",
        "Moran, Mr. James"
    ],
    "Sex": ["male", "female", "female", "female", "male", "male"],
    "Age": [22, 38, 26, 35, 35, None],
    "SibSp": [1, 1, 0, 1, 0, 0],
    "Parch": [0, 0, 0, 0, 0, 0],
    "Ticket": ["A/5 21171", "PC 17599", "STON/O2. 3101282", "113803", "373450", "330877"],
    "Fare": [7.25, 71.2833, 7.925, 53.1, 8.05, 8.4583],
    "Cabin": [None, "C85", None, "C123", None, None],
    "Embarked": ["S", "C", "S", "S", "S", "Q"]
}
df = pd.DataFrame(data)

async def main():
    project_id = "1"
    steps = [
        {"preprocessing_step": "dropna", "target_columns": {"subset": ["Age"]}},
        {"preprocessing_step": "fillna", "target_columns": {"value": {"Cabin": "Unknown"}}},
        {"preprocessing_step": "encode", "target_columns": {"columns": ["Sex", "Embarked"]}},
        {"preprocessing_step": "normalize", "target_columns": {"columns": ["Fare"]}}
    ]
    result = await generate_preprocessing(project_id, steps)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
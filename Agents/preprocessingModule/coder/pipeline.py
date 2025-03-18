from typing_extensions import TypedDict, Annotated, NotRequired
from typing import Literal, Dict
from ..pipeline import PreprocessingState
import operator
from langgraph.graph import StateGraph, START
from .generator import generator_node
from .checker import checker_node
from .reflector import reflector_node
from langchain_core.messages import AnyMessage

class CoderState(TypedDict):
    """State management for preprocessing code generation pipeline"""
    messages: Annotated[list[AnyMessage], operator.add]
    generation: NotRequired[dict]
    iterations: NotRequired[int]
    error: NotRequired[str]
    project_id: str
    current_step: dict
    data_report: NotRequired[dict]
    transformed_data: NotRequired[dict]
    transformers: NotRequired[dict]
    parallel_context: NotRequired[Dict]

CONFIG = {
    'MAX_ITERATIONS': 3,
    'ENABLE_REFLECTION': True
}

def decide_to_continue(state) -> Literal["generator", "reflector", "__end__"]:
    """Determine next step based on validation results"""
    iterations = state.get("iterations", 0)
    error = state.get("error")
    
    # Termination conditions
    if not error or iterations >= CONFIG['MAX_ITERATIONS']:
        return "__end__"
    
    # Simple reflection switch
    if CONFIG['ENABLE_REFLECTION']:
        return "reflector"
    
    return "generator"

async def process_code_step(state: PreprocessingState):
    """Handle code steps in parallel context"""
    context = {
        "dataset": state["dataset_state"].copy(),
        "transformers": state["transformers"].copy()
    }
    
    result = await coder_workflow.ainvoke({
        **state,
        "parallel_context": context
    })
    
    return {
        "dataset_state": result["dataset_state"],
        "transformers": result["transformers"],
        "logs": result["logs"],
        "errors": result["errors"]
    }

workflow = StateGraph(CoderState)
workflow.add_node("generator", generator_node)
workflow.add_node("checker", checker_node)
workflow.add_node("reflector", reflector_node)

workflow.add_edge(START, "generator")
workflow.add_edge("generator", "checker")
workflow.add_conditional_edges(
    "checker",
    decide_to_continue,
    {
        "generator": "generator",
        "reflector": "reflector",
        "__end__": "__end__"
    }
)
workflow.add_edge("reflector", "generator")

coder_workflow = workflow.compile()
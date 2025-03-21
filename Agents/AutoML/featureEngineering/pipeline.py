from typing_extensions import TypedDict
from typing_extensions import TypedDict,Annotated,NotRequired
from langchain_core.messages import AnyMessage
import operator
from langgraph.graph import StateGraph, START
from .generator import generator_node
from .checker import checker_node
from .planner import planner_node 
from typing import Literal

CONFIGURATIONS={
    'FLAG':'do not reflect',
    'MAX_ITERATIONS': 3
}
class FeatureEngineeringState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        error : Binary flag for control flow to indicate whether test error was tripped
        messages : With user question, error messages, reasoning
        generation : Code solution
        iterations : Number of tries
    """
    feature_engineering_logic: NotRequired[str]
    messages: Annotated[list[AnyMessage], operator.add]
    generation: str
    iterations: NotRequired[int] = 0
    error: NotRequired[str] = ''
    project_id:str
    data_report: NotRequired[str]
    successful_features: Annotated[list[str], operator.add]


def decide_to_finish(state)->Literal["generator", "__end__"]:
    """
    Determines whether to finish.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    error = state["error"]
    if 'iterations' in state:
        iterations = state["iterations"]
    else:
        iterations = 0 

    if error == "no" or iterations == CONFIGURATIONS["MAX_ITERATIONS"]:
        print("---DECISION: FINISH---")
        return "__end__"
    else:
        print("---DECISION: RE-TRY SOLUTION---")
        return "generator"
    
workflow = StateGraph(FeatureEngineeringState)
# Define the nodes
workflow
workflow.add_node("planner", planner_node)  # plan/generate ideas
workflow.add_node("generator", generator_node)  # generation solution
workflow.add_node("checker", checker_node)  # check code

# Build graph
workflow.add_edge(START, "planner")
workflow.add_edge("generator", "checker")
workflow.add_conditional_edges("checker",decide_to_finish)
coder = workflow.compile()

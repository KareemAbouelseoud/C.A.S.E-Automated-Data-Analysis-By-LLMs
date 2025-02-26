import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing_extensions import TypedDict
from typing_extensions import TypedDict,Annotated,NotRequired
from langchain_core.messages import AnyMessage
import operator
from langgraph.graph import END, StateGraph, START
from evaluator import evaluator_node
from typing import Literal

CONFIGURATIONS={
    'MAX_ITERATIONS': 3
}


class CoderState(TypedDict):
    """
    Represents the state of our graph.
    """

    messages: Annotated[list[AnyMessage], operator.add]
    generation: str
    iterations: NotRequired[int] = 0
    error: NotRequired[str] = 'no'
    models_completed: NotRequired[int] = 0
    project_id:str # Project ID
    mode: str # Mode Selected by the User
    problem_type: NotRequired[str] # Problem Type Identified by the LLM
    splitting_logic: NotRequired[str] # Splitting Steps Documented for the User and rest of Agents
    X_test: NotRequired[object] # testing Features
    y_test: NotRequired[object] # testing Target

    preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    models: NotRequired[list] # Model Names Selected by LLM
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)

    
    
def decide_to_finish(state)->Literal["evaluator", "_end_"]:
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

    ModelsCompleted= 1 if state['mode']=='HERMES' else 3 if state['mode']=='ATHENA' else 5

    if (error == "no" or iterations == CONFIGURATIONS["MAX_ITERATIONS"]) and int(state["models_completed"]) == ModelsCompleted:
        print("---DECISION: FINISHED EVALUATION---")
        return END
    else:
        if  int(state["models_completed"]) != ModelsCompleted:
            print("---EVALUATING NEXT MODEL---")
        else:
            print("---DECISION: RE-TRY EVALUATION---")

        return "evaluator"


workflow = StateGraph(CoderState)
# Define the nodes
workflow.add_node("evaluator", evaluator_node)  # check code

# Build graph
workflow.add_edge(START, "evaluator")
workflow.add_conditional_edges("evaluator",decide_to_finish)
coder = workflow.compile()
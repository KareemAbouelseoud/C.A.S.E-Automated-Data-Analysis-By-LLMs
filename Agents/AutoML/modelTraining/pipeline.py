import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing_extensions import TypedDict
from typing_extensions import TypedDict,Annotated,NotRequired
from langchain_core.messages import AnyMessage
import operator
from langgraph.graph import END, StateGraph, START
from modelTraining.trainer import trainer_node
from typing import Literal

CONFIGURATIONS={
    'FLAG':'do not reflect',
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
    X_train: NotRequired[object] # Training Features
    y_train: NotRequired[object] # Training Target

    preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    models: NotRequired[list] # Model Names Selected by LLM
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)

    
    
def decide_to_finish(state)->Literal["trainer", "__end__"]:
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

    if iterations == 0:
        if state['models_completed']>=ModelsCompleted:
            return END
        else:
            return "trainer"
    elif error == "yes" and iterations != 0:
        return "trainer"
        

workflow = StateGraph(CoderState)
# Define the nodes
workflow.add_node("trainer", trainer_node)  # check code

# Build graph
workflow.add_edge(START, "trainer")
workflow.add_conditional_edges("trainer",decide_to_finish)
model_trainer_node = workflow.compile()
from typing_extensions import TypedDict, Annotated, NotRequired
from langchain_core.messages import AnyMessage
import operator
from langgraph.graph import StateGraph, START
from .generator import generator_node
from .checker import checker_node
from .reflector import reflector_node
from typing import Literal
import pandas as pd
from typing_extensions import Any


CONFIGURATIONS = {
    'FLAG': 'reflect',
    'MAX_ITERATIONS': 3
}

class CoderState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        error : Binary flag for control flow to indicate whether test error was tripped
        messages : With user question, error messages, reasoning
        generation : List of code solutions for all tasks
        iterations : Number of tries
        preprocessing_tasks : The task to process
        target_column : The column to process
        strategy : The strategy to use
        generated_errors : List of code solutions that failed validation
        executed_responses : List of successfully executed code solutions
    """
    messages: Annotated[list[AnyMessage], operator.add]
    generation: list[dict]  # List of code solutions
    iterations: NotRequired[int] = 0
    error: NotRequired[str] = ''
    project_id: str
    data_report: NotRequired[str]
    dataframe: NotRequired[str]  # Store as JSON string, not pandas.DataFrame
    preprocessed_dataframe: NotRequired[str]
    preprocessing_tasks: NotRequired[str]  # The task to process
    target_column: NotRequired[str]  # The column to process
    strategy: NotRequired[str]  # The strategy to use
    generated_errors: NotRequired[list[dict]] = []  # Code that failed validation
    executed_responses: NotRequired[list[dict]] = []  # Successfully executed code

def decide_to_finish(state) -> Literal["generator", 'reflector', "__end__"]:
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

    #debugger
    print(f"---DEBUG: Iteration: {iterations}, Error: {error}---")

    if error == "no":
        print("---DECISION: TASK COMPLETED---")        
        # If task is processed and no errors, finish
        return "__end__"
    elif iterations >= CONFIGURATIONS["MAX_ITERATIONS"]:
        print("---DECISION: MAX ITERATIONS REACHED---")
        return "__end__"
    else:
        print("---DECISION: RE-TRY SOLUTION---")
        if state.get("generated_errors") and CONFIGURATIONS["FLAG"] == "reflect":
            return "reflector"
        else:
            return "generator"

workflow = StateGraph(CoderState)
# Define the nodes
workflow.add_node("generator", generator_node)  # generation solution
workflow.add_node("checker", checker_node)  # check code
workflow.add_node("reflector", reflector_node)  # reflect

# Build graph
workflow.add_edge(START, "generator")
workflow.add_edge("generator", "checker")
workflow.add_conditional_edges("checker", decide_to_finish)
workflow.add_edge("reflector", "generator")
coder_pipeline = workflow.compile()
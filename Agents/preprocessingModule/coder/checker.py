from API.Requests.projectRequests import get_dataset
import numpy as np
import pandas as pd
import re


async def checker_node(state):
    """
    Check code

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """

    print("---CHECKING CODE---")

    # State
    messages = state["messages"]
    code_solution = state["generation"]
    iterations = state["iterations"]

    # Get solution components
    imports = code_solution.imports
    code = code_solution.code

    # Check imports
    try:
        exec(imports)
    except Exception as e:
        print("---CODE IMPORT CHECK: FAILED---")
        error_message = [("user", f"Your solution failed the import test: {e}")]
        messages += error_message
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "yes",
        }

    # Check execution
    try:
        dataframe = await get_dataset(state['project_id'])
        # Create a copy of the dataframe for preprocessing
        df = dataframe.copy()
        globals_dict = {'df': df}
        print("CODE:", imports + "\n" + code)
        exec(imports + "\n" + code, globals_dict)
        
        # Save the preprocessed dataframe in the state
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "no",
            "preprocessed_dataframe": df
        }
        
    except Exception as e:
        print("---CODE BLOCK CHECK: FAILED---")
        error_message = [("user", f"Your solution failed the code execution test: {e}")]
        messages += error_message
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "yes",
        }
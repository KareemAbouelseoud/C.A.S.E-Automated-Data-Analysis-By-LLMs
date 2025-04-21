from API.Requests.projectRequests import get_dataset
import numpy as np
import pandas as pd
import re


async def checker_node(state):
    """
    Check code with robust data validation and error handling

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updated state with error information
    """
    print("---CHECKING CODE---")

    # State unpacking with validation
    messages = state.get("messages", [])
    code_solution = state.get("generation")
    iterations = state.get("iterations", 0)

    if not code_solution or not hasattr(code_solution, "imports") or not hasattr(code_solution, "code"):
        return {
            "generation": None,
            "messages": messages + [("user", "Invalid code solution format")],
            "error": "yes",
            "iterations": iterations
        }

    # Check imports with isolation
    try:
        print(f"Checking imports: {code_solution.imports}")
        exec(code_solution.imports, {})
    except Exception as e:
        error_msg = f"Import check failed: {str(e)}"
        print(f"---IMPORT CHECK FAILED: {error_msg}---")
        return {
            "generation": code_solution,
            "messages": messages + [("user", error_msg)],
            "iterations": iterations,
            "error": "yes"
        }

    # Data validation pipeline
    try:
        # dataset
        dataframe = await get_dataset(state['project_id'])
        
        # dataset existence
        if dataframe is None:
            raise ValueError("Dataset fetch returned None")
            
        #  DataFrame type
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(f"Expected DataFrame, got {type(dataframe)}")
            
        # Validate DataFrame content
        if dataframe.empty:
            raise ValueError("Dataset is empty")
            
        #  copy
        df = dataframe.copy()
        globals_dict = {'df': df}

        # Execute code with isolation
        print(f"Executing code:\n{code_solution.imports}\n{code_solution.code}")
        exec(f"{code_solution.imports}\n{code_solution.code}", globals_dict)
        
        #  Validate 
        processed_df = globals_dict.get('df', None)
        if not isinstance(processed_df, pd.DataFrame):
            raise TypeError("Code did not produce a valid DataFrame")
            
        if processed_df.empty:
            raise ValueError("Processing resulted in empty DataFrame")

        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "no",
            "preprocessed_dataframe": processed_df
        }

    except Exception as e:
        error_msg = f"Code execution failed: {str(e)}"
        print(f"---EXECUTION FAILED: {error_msg}---")
        return {
            "generation": code_solution,
            "messages": messages + [("user", error_msg)],
            "iterations": iterations,
            "error": "yes"
        }
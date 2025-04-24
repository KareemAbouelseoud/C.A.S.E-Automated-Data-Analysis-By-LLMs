import numpy as np
import pandas as pd
import re


async def checker_node(state):
    """
    Check all generated code solutions with robust data validation and error handling

    Args:
        state (dict): The current graph state containing:
            - generation: List of generated code solutions
            - preprocessing_tasks: The task being processed
            - target_column: The column being processed
            - strategy: The strategy being used
            - dataframe: The input DataFrame
            - messages: List of messages in the conversation

    Returns:
        state (dict): Updated state with validation results
    """
    print("---CHECKING CODE SOLUTIONS---")

    # State unpacking with validation
    messages = state["messages"]
    generated_solutions = state["generation"]
    iterations = state["iterations"]
    preprocessing_tasks = state["preprocessing_tasks"]
    target_column = state["target_column"]
    strategy = state["strategy"]

    if not generated_solutions:
        return {
            "generation": [],
            "messages": messages + [("user", "No code solutions to check")],
            "error": "yes",
            "iterations": iterations,
            "preprocessing_tasks": preprocessing_tasks,
            "target_column": target_column,
            "strategy": strategy,
            "generated_responses": [],
            "generated_errors": [],
            "executed_responses": []
        }

    # Initialize lists for results
    generated_responses = []
    generated_errors = []
    executed_responses = []
    processed_df = state["dataframe"].copy()

    # Check each solution
    for solution in generated_solutions:
        code_solution = solution["solution"]
        current_task = solution["task"]

        try:
            # Check imports with isolation
            print(f"Checking imports for task: {code_solution.imports}")
            exec(code_solution.imports, {})

            # Execute code with isolation
            print(f"Executing code:\n{code_solution.imports}\n{code_solution.code}")
            globals_dict = {'df': processed_df}
            exec(f"{code_solution.imports}\n{code_solution.code}", globals_dict)
            
            # Validate result
            result_df = globals_dict["df"]
            if not isinstance(result_df, pd.DataFrame):
                raise TypeError("Code did not produce a valid DataFrame")
            if result_df.empty:
                raise ValueError("Processing resulted in empty DataFrame")

            # Update processed dataframe and add to executed responses
            processed_df = result_df
            executed_responses.append({
                "solution": code_solution,
                "task": current_task
            })

        except Exception as e:
            error_msg = f"Code execution failed: {str(e)}"
            print(f"---EXECUTION FAILED: {error_msg}---")
            generated_errors.append({
                "solution": code_solution,
                "task": current_task,
                "error": error_msg
            })

    # Determine if we have any errors
    has_errors = len(generated_errors) > 0

    return {
        "generation": generated_solutions,
        "iterations": iterations,
        "error": "no" if not has_errors else "yes",
        "generated_responses": generated_responses,
        "generated_errors": generated_errors,
        "executed_responses": executed_responses,
        "preprocessed_dataframe": processed_df
    }
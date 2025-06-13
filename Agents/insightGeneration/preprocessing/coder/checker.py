import pandas as pd
import json
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
        preprocessed_dataframe: The processed dataframe (JSON string)
        messages: List of messages in the conversation
        error: Error status
        executed_responses: List of successfully executed code solutions
        generated_errors: List of failed code solutions
    """
    print("---CHECKING CODE SOLUTIONS---")

    # State unpacking with validation
    messages = state["messages"]
    generated_solutions = state["generation"]
    iterations = state["iterations"]
    preprocessing_tasks = state["preprocessing_tasks"]
    target_column = state["target_column"]
    strategy = state["strategy"]
    dataframe = state["dataframe"]

    #prepare the globals with input DataFrame as JSON string
    dataframe_json_str = dataframe.to_json()
    globals_dict = {'df': dataframe_json_str}

    if not generated_solutions:
        return {
            "generation": [],
            "messages": messages + [("user", "No code solutions to check")],
            "error": "yes",
            "iterations": iterations,
            "preprocessing_tasks": preprocessing_tasks,
            "target_column": target_column,
            "strategy": strategy,
            "generated_errors": [],
            "executed_responses": []
        }

    # Initialize lists for results
    generated_errors = []
    executed_responses = []
    result_json = dataframe_json_str  # fallback in case no execution happens

    # Check each solution
    for idx, solution in enumerate(generated_solutions):
        code_solution = solution["solution"]
        current_task = solution["task"]

        try:
            # Check imports with isolation
            print(f"Checking imports for task: {code_solution.imports}")
            exec(code_solution.imports, {})

            # Execute code with isolation
            print(f"Executing code:\n{code_solution.imports}\n{code_solution.code}")
            exec(f"{code_solution.imports}\n{code_solution.code}", globals_dict)

            # Validate result
            result_json = globals_dict["df"]
            if not isinstance(result_json, str):
                raise TypeError("Code did not produce a JSON string")

            try:
                result_df = pd.read_json(result_json)
            except Exception as e:
                raise ValueError(f"Failed to parse JSON string to DataFrame: {e}")

            if result_df.empty:
                raise ValueError("Processing resulted in empty DataFrame")

            # Update processed dataframe and add to executed responses
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
                "error": error_msg,
                "task_index": idx
            })

    # Determine if we have any errors
    has_errors = len(generated_errors) > 0

    #Print DataFrame summaries
    print("Preprocessed dataframe before code execution:")
    print(pd.read_json(dataframe_json_str).describe())

    print("Preprocessed dataframe after code execution:")
    try:
        print(pd.read_json(result_json).describe())
    except Exception as e:
        print(f"Could not describe result DataFrame due to error: {e}")

    return {
        "generation": generated_solutions,
        "iterations": iterations,
        "error": "no" if not has_errors else "yes",
        "generated_errors": generated_errors,
        "executed_responses": executed_responses,
        "preprocessed_dataframe": result_json  # return as JSON string
    }

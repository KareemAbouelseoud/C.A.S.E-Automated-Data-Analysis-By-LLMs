from API.Requests.projectRequests import get_dataset
import numpy as np
import pandas as pd
import json
import inspect
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
    code_solution_list = json.loads(state["generation"])
    iterations = state["iterations"]
    error=False
    df=await get_dataset(state['project_id'])
    successful_features=[]
    for code_solution in code_solution_list:
        imports = code_solution["imports"]
        code = code_solution["code"]
        # Check imports
        try:
            exec(imports)
        except Exception as e:
            print("---CODE IMPORT CHECK: FAILED---")
            error_message = [("user", f"YOUR CODE: {imports}\n{code} \n Your solution failed the import test: {e}")]
            messages += error_message
            error=True
            continue

        # Check execution
        try:
            context={}
            exec(imports + "\n" + code,context)
            functions = {name: obj for name, obj in context.items() if inspect.isfunction(obj)}
            
            for func_name, func in functions.items():
                if 'df' in inspect.signature(func).parameters:
                    func(df)
                    successful_features.append(code_solution)
                    

        except Exception as e:
            print("---CODE BLOCK CHECK: FAILED---")
            print(f"YOUR CODE: {imports}\n{code}")
            error_message = [("user", f"YOUR CODE: {imports}\n{code} \n Your solution failed the code execution test: {e}")]
            messages += error_message
            error=True
            continue

    # No errors
    print("---NO CODE TEST FAILURES---")
    return {
        "generation": code_solution,
        "messages": messages,
        "iterations": iterations,
        "error": "no" if not error else "yes",
        "successful_features":successful_features
    }


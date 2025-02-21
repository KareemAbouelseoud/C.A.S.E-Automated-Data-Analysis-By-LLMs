from Database import mainDatabase
from Backend.services.project_service import ProjectService
_project_service=ProjectService()
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
        df= await _project_service.fetch_dataset(state['project_id'])
        globals_dict={'_project_service':_project_service,
                      'project_id':state['project_id'],
                      'df':df}
        print("CODE:", imports + "\n" + code)
        exec(imports + "\n" + code,globals_dict)
        if 'fig_dict' in  globals_dict:
            if not isinstance(globals_dict['fig_dict'],dict):
                error_message = [("user", f"Your solution failed because there is no variable called fig_dict or because it is not a dictionary")]
                messages += error_message
                return {
                    "generation": code_solution,
                    "messages": messages,
                    "iterations": iterations,
                    "error": "yes",
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

    # No errors
    print("---NO CODE TEST FAILURES---")
    return {
        "generation": code_solution,
        "messages": messages,
        "iterations": iterations,
        "error": "no",
        'visualization':[globals_dict['fig_dict']],
    }

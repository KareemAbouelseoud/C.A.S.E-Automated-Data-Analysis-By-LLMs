from Database import mainDatabase
def evaluator_node(state):
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
    X_train = state["X_train"]
    y_train = state["y_train"]
    project_id = state["project_id"]

    # Get solution components
    evaluator_logic = code_solution.prefix
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
        df=mainDatabase.fetch_dataset(state['project_id'])
        preprocessing_pipeline=mainDatabase.fetch_pipeline(project_id)

        globals_dict={'mainDatabase':mainDatabase,
                      'project_id':state['project_id'],
                      'df':df,
                      'X_train':X_train,
                      'y_train':y_train,
                      'preprocessing_pipeline':preprocessing_pipeline}
        print("CODE:", imports + "\n" + code)
        exec(imports + "\n" + code,globals_dict)
        if 'model' in  globals_dict:
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


    model=globals_dict['model']

    # Save the model to the database

    mainDatabase.save_model(project_id, model,state['model'][state['models_completed']]['model'])
    print("---MODEL SAVED SUCCESSFULLY---")


    # No errors
    print("---NO CODE TEST FAILURES---")
    return {
        "generation": code_solution,
        "messages": messages,
        "iterations": iterations,
        "error": "no",
        "evaluator_logic": evaluator_logic,
        'models_completed':globals_dict['models_completed']+1,
    }
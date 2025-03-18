from API.Requests.projectRequests import get_dataset, update_dataset
import numpy as np
import pandas as pd

async def checker_node(state):
    """
    Validate generated preprocessing code
    
    Args:
        state (dict): Current graph state
        
    Returns:
        state (dict): Updated state with validation results
    """
    
    print("---VALIDATING PREPROCESSING CODE---")
    
    messages = state["messages"]
    code_solution = state["generation"]
    iterations = state["iterations"]
    project_id = state["project_id"]
    
    original_df = await get_dataset(project_id)
    test_df = original_df.copy()
    
    # Validate imports
    try:
        exec(code_solution.imports, globals())
    except Exception as e:
        print("---IMPORT CHECK FAILED---")
        return {
            **state,
            "messages": messages + [("user", f"Import error: {str(e)}")],
            "error": "import_failure"
        }
        
    try:
        exec_globals = {'df': test_df.copy()}
        exec(code_solution.code, exec_globals)
        transformed_df = exec_globals['df']
        
        # Validate dataframe integrity
        if not isinstance(transformed_df, pd.DataFrame):
            raise ValueError("Code must return a pandas DataFrame")
            
        if transformed_df.shape[0] != original_df.shape[0]:
            raise ValueError("Row count changed during transformation")
            
        await update_dataset(project_id, transformed_df)
        
    except Exception as e:
        print("---EXECUTION CHECK FAILED---")
        return {
            **state,
            "messages": messages + [("user", f"Execution error: {str(e)}")],
            "error": "execution_failure"
        }
    
    print("---CODE VALIDATION SUCCESSFUL---")
    return {
        **state,
        "transformed_data": make_serializable(transformed_df.head()),
        "error": None
    }

def make_serializable(obj):
    """Convert pandas/numpy objects to native Python types"""
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, pd.Series):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    return obj
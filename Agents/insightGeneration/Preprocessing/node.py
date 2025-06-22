from .config import *
async def preprocessor_executor_node(state: Dict):
    """
    This function is a placeholder for the preprocessor executor node.
    It is intended to be used in a state graph for preprocessing tasks.
    
    Returns:
        str: A message indicating that the preprocessor executor node is called.
    """
    try:
    
        # df = pd.read_json(StringIO())
        recommendation = state.get("recommendation")
        if isinstance(recommendation, dict):
            recommendation = [recommendation]

        preprocessing_tasks = []
        for item in recommendation:
            steps = item.get("args", {}).get("preprocessing_steps", [])
            for step in steps:
                if not all(k in step for k in ("preprocessing_step", "column_name")):
                    print(f"[WARNING] Skipping malformed step: {step}")
                    continue
                preprocessing_tasks.append({
                    "task": step["preprocessing_step"],
                    "column": step["column_name"],
                    "strategy": step["explanation"] if "explanation" in step else " "
                })
        # wrapped_recommendation = [{"args": recommendation}]  
        result= await preprocess_data("1", state['df'], preprocessing_tasks)
        return {"df":result["preprocessed_dataframe"].to_json()}

    except Exception as e:
        raise Exception(f"Error in preprocessor_executor_node: {str(e)}")
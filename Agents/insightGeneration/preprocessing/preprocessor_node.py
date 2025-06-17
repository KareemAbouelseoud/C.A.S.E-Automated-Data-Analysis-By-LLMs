from preprocessing.pipeline import preprocess_data
import pandas as pd
from io import StringIO
from preprocessing.pipeline import preprocess_data

async def preprocessor_executor_node(state):
 
  
    df = state.get("df")
    # Ensure df is a JSON string before passing to preprocess_data
    if isinstance(df, pd.DataFrame):
        df = df.to_json(orient="records")
    recommendation = state.get("recommendation")
    result = await preprocess_data("1", df, recommendation)
    # Ensure preprocessed_dataframe is always a JSON string
    preprocessed = result.get("preprocessed_dataframe")
    if isinstance(preprocessed, pd.DataFrame):
        preprocessed = preprocessed.to_json(orient="records")
    elif not isinstance(preprocessed, str):
        # Try to convert to string if possible
        try:
            preprocessed = str(preprocessed)
        except Exception:
            preprocessed = ""
    result["preprocessed_dataframe"] = preprocessed
    print ("preprocessing done")

    # state["num_iterations"]+=1

    return {"df":result["preprocessed_dataframe"] ,"num_iterations": state["num_iterations"]}



# async def preprocessor_executor_node(state):
#     try:
        
#         df = pd.read_json(StringIO(state['df']))
#         recommendation = state.get("recommendation")
#         # wrapped_recommendation = [{"args": recommendation}]  
#         result = await preprocess_data("1", df, recommendation)
#         preprocessed_df = result.get("preprocessed_dataframe")
#         print ("preprocessing done")
#         # messages = result.get("messages", [])
#         # executed = result.get("executed_responses", [])

#         return { "df": preprocessed_df }
#     except Exception as e:
        
#         return { "error": str(e)}


def restart_pipeline(state):
    if  state.get("num_iterations")==1 :
        print("rerunning pipeline,num_iterations:", state.get("num_iterations"))
        return "Report_Node"
    else:
        print("Finalizing output,num_iterations:", state.get("num_iterations"))
        return "Finalize_output"
    

# "messages": messages,# "executed_responses": executed,
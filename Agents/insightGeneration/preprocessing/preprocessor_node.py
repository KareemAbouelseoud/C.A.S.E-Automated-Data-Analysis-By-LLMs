
from preprocessing.pipeline import preprocess_data
import pandas as pd
from io import StringIO
from preprocessing.pipeline import preprocess_data

# async def preprocessor_executor_node(state):
 
  
#     df = state.get("df")
#     recommendation = state.get("recommendation")
#     result = await preprocess_data("1", df, recommendation)
#     if isinstance(result.get("preprocessed_dataframe"), pd.DataFrame):
#         result["preprocessed_dataframe"] = result["preprocessed_dataframe"].to_json(orient="records")

#     print ("preprocessing done")
#     state["num_iterations"]+=1

#     return {"num_iterations": state["num_iterations"]}

from preprocessing.pipeline import preprocess_data  # your actual import path

async def preprocessor_executor_node(state):
    try:
        
        df = pd.read_json(StringIO(state['df']))
        recommendation = state.get("recommendation")
        # wrapped_recommendation = [{"args": recommendation}]  
        result = await preprocess_data("1", df, recommendation)
        preprocessed_df = result.get("preprocessed_dataframe")
        print ("preprocessing done")
        # messages = result.get("messages", [])
        # executed = result.get("executed_responses", [])

        return { "df": preprocessed_df }
    except Exception as e:
        
        return { "error": str(e)}


def restart_pipeline(state):
    if  state.get("num_iterations")==1 :
        print("rerunning pipeline,num_iterations:", state.get("num_iterations"))
        return "qugen_node"
    else:
        print("Finalizing output,num_iterations:", state.get("num_iterations"))
        return "Finalize_output"
    

# "messages": messages,# "executed_responses": executed, 
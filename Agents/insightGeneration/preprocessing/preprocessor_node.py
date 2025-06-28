
import pandas as pd
from io import StringIO
from preprocessing.pipeline import preprocess_data
import json
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd


# async def preprocessor_executor_node(state):
  
#        dataframe=state["df"]
#        recommendation=state["recommendation"]
#        result = await preprocess_data("1",dataframe,recommendation)
#        result["preprocessed_dataframe"] = result["preprocessed_dataframe"] .to_json(orient="records")
       
#        return { "new_df":  result["preprocessed_dataframe"] }
  
    

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}


llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

async def preprocessor_node(state):
    """
    Preprocessor node that uses a pandas agent to apply
    preprocessing steps directly to a dataframe .
    """

    # get the dataframe
    df_json = state["df"]
    if isinstance(df_json, str):
        df = pd.read_json(StringIO(df_json), orient="records")
    else:
        df = df_json

    # parse recommendations
    recommendations = state.get("recommendation", [])
    if isinstance(recommendations, dict):
        recommendations = [recommendations]

    # collect preprocessing tasks
    preprocessing_tasks = []
    for item in recommendations:
        steps = item.get("args", {}).get("preprocessing_steps", [])
        for step in steps:
            if not all(k in step for k in ("preprocessing_step", "column_name")):
                print(f"[WARNING] Skipping malformed step: {step}")
                continue
            preprocessing_tasks.append({
                "task": step["preprocessing_step"],
                "column": step["column_name"],
                "strategy": step.get("explanation", " ")
            })

    # build prompt
    instruction_parts = []
    for task in preprocessing_tasks:
        instruction_parts.append(
            f"{task['task']} on column '{task['column']}' because {task['strategy']}"
        )
    instruction_text = "\n".join(instruction_parts)

    command = f"""
Please apply the following preprocessing steps on the dataframe in memory:
{instruction_text}

Only modify the dataframe directly, do not return any JSON.
    """

    # run the pandas dataframe agent
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True
    )

    await agent.ainvoke(command)

    # store back to state
    print("Preprocessed dataframe preview:")
    print(df.head())
    
    state["df"] = df.to_json(orient="records")
   
   
    return state


def restart_pipeline(state):
    if  state.get("num_iterations")==1 :
        print("rerunning pipeline,num_iterations:", state.get("num_iterations"))
        return "Report_Node"
    else:
        print("Finalizing output,num_iterations:", state.get("num_iterations"))
        return "Finalize_output"
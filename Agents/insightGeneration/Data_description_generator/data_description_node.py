from io import StringIO
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from models import DataDescription
    

def data_description_prompt(df, feedback):
    return f"""
    Human Feedback: {feedback[-1] if feedback else 'No feedback yet'}
       Given the dataset:
        {df}
        Consider previous human feedback to refine the response. 
        Provide the following:
        1. explanation of each column in bullet points.
        2. An overview description of the dataset.
        3. Key patterns in the data distribution.
        4. Notable data quality issues.
        """
        

def data_description_generator_node(state):
    """
    Generates or refines the dataset description considering human feedback if provided.
    """
    CONFIGURATIONS={
        'temperature':0.0,
        'model':"gemini-2.0-flash",
        'number of retries':3
    }
    llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
    if "df" not in state:
        raise ValueError("No dataset provided in state.")

    df = state["df"]
    temp_df=pd.read_json(StringIO(df))
    feedback = state.get("human_feedback", ["No feedback yet"])
    prompt=data_description_prompt(df, feedback)
    
  
    structured_llm = llm.with_structured_output(DataDescription, include_raw=False)
    response = structured_llm.invoke(prompt)

    description = response

    print(f"Current description:\n{response}\n")
    schema = [col.lower() for col in temp_df.columns.tolist()]

    return {"description": response, "human_feedback": feedback, "schema":schema }


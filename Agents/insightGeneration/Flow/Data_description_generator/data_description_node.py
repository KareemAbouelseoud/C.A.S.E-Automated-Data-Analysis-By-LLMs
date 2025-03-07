from typing import Dict
from genai_config import model,llm
from pydantic import BaseModel, Field
import pandas as pd
from io import StringIO
from langchain import hub
from langsmith import Client


class DataDescription(BaseModel):
    """ Structured output schema for data description node. """
   
    col_explanation: str = Field(description="explanation of each column")
    overview:str=Field(description="overview description of the dataset")
    key_patterns: str=Field(description="Key patterns in the data distribution")
    qual_issues:str=Field(description="Notable data quality issues in dataset")
    

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

    if "df" not in state:
        raise ValueError("No dataset provided in state.")

    df = state["df"]
    feedback = state.get("human_feedback", ["No feedback yet"])
    prompt=data_description_prompt(df, feedback)
    
  
    structured_llm = llm.with_structured_output(DataDescription, include_raw=False)
    response = structured_llm.invoke(prompt)

    description = response

    print(f"Current description:\n{response}\n")
    


    return {"description": response, "human_feedback": feedback}


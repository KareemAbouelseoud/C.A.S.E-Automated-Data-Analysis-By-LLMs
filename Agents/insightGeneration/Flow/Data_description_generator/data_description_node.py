from typing import Dict
from genai_config import model,llm
from pydantic import BaseModel, Field
import pandas as pd
from io import StringIO
from langchain import hub
from langsmith import Client
from langchain.prompts import SystemMessagePromptTemplate
class DataDescription(BaseModel):
    """ Structured output schema for data description node. """
   
    col_explanation: str = Field(description="explanation of each column")
    overview:str=Field(description="overview description of the dataset")
    key_patterns: str=Field(description="Key patterns in the data distribution")
    qual_issues:str=Field(description="Notable data quality issues in dataset")
    
# system_prompt = hub.pull("data-description-prompt").messages[0].prompt.template
# from langsmith import Client
# client = Client(api_key="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")
# prompt = client.pull_prompt("data_description_prompt", include_model=True)
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



class DataDescription(BaseModel):
    """Structured output schema for data description node."""
    col_explanation: str = Field(description="Explanation of each column")
    overview: str = Field(description="Overview description of the dataset")
    key_patterns: str = Field(description="Key patterns in the data distribution")
    qual_issues: str = Field(description="Notable data quality issues in dataset")

def data_description_generator_node(state):
    """
    Generates or refines the dataset description considering human feedback if provided.
    """

    if "df" not in state:
        raise ValueError("No dataset provided in state.")

    df = state["df"]
    feedback = state.get("human_feedback", [])

    if not feedback:  
        feedback.append("No feedback yet")

    # Pull the prompt template
    system_prompt_template = hub.pull("data_description_prompt").messages[0]

    # Ensure it's a PromptTemplate before formatting
    if isinstance(system_prompt_template, SystemMessagePromptTemplate):
        system_prompt = system_prompt_template.format(df=df, feedback=feedback[-1])
    else:
        raise TypeError("Expected a PromptTemplate, but got a different object.")

    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        response = llm.invoke(messages)

        structured_llm = llm.with_structured_output(DataDescription, include_raw=False)
        structured_response = structured_llm.invoke(response)

        print(f"Current description:\n{structured_response}\n")

        return {"description": structured_response, "human_feedback": feedback}

    except Exception as e:
        print(f"Error in description_node: {str(e)}")
        raise


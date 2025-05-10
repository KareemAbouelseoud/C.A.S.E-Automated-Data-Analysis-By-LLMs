from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List
import re

CONFIGURATIONS={
    'temperature':0.0,
    'model':"gemini-2.0-flash",
    'number of retries':3
}
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

def recommender_prompt(df, insight_cards):
    return f"""
Given the following dataset {df} and insight cards {insight_cards}:
Recommend 
1 - preprocessing steps to be applied on the dataset for generating better quality insights.
2 - the columns this preprocessing step should be applied to.
3 - the explanation why this preprocessing step is needed and how it will generate better quality insights.


"""

recommender_schema = {
    "name": "preprocessing_recommender", 
    "description": "Recommend preprocessing steps for better insight generation",
    "parameters": {
        "type": "object",
        "properties": {
            "preprocessing_steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "preprocessing_step": {
                            "type": "string",
                            "description": "The name of the preprocessing step"
                        },
                        "column_name": {
                            "type": "string",
                            "description": "The name of the column that this preprocessing step will be applied to"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Why this preprocessing step is applied"
                        }
                    },
                    "required": ["preprocessing_step", "column_name", "explanation"]
                }
            }
        },
        "required": ["preprocessing_steps"]
    }
}



def recommender_node (state):

    df = state["df"]
    insight_cards=state["advanced_insight_cards"]
    prompt=recommender_prompt(df,insight_cards)
    structured_llm = llm.with_structured_output(recommender_schema)
    response = structured_llm.invoke(prompt)
    print(response)

    return  {"recommendation": response}


    
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




    
# class Recommender(BaseModel):
#     """ Structured output schema for recommender node. """
#     preprocessing_steps: str= Field(description="preprocessing steps required for better insight generation ")
#     column_name: str = Field(description="the name of the column that these preprocessing step will be applied")
#     explanation: str=Field(description="reasoning of why this preprocessing step will be applied")

def recommender_node (state):
    df = """
    AthleteID,	SportType,	Height,	Weight,	Age, PerformanceScore
    1,	Swimming,	189,	107,	50,	49
    2,	Handball,	192,	115,	17,	41
    3,	Swimming,	211,	82,	28,	87

    """
    insight_cards = [
    {
        "title": "Highest Performance Score",
        "content": "Athlete 3 in Swimming has the highest Performance Score of 87."
    },
    {
        "title": "Youngest Athlete",
        "content": "Athlete 2 is the youngest at 17 years old and plays Handball."
    },
    {
        "title": "Tallest Athlete",
        "content": "Athlete 3 is the tallest with a height of 211 cm."
    },
    {
        "title": "Heaviest Athlete",
        "content": "Athlete 2 is the heaviest, weighing 115 kg."
    },
    {
        "title": "Sport Distribution",
        "content": "Swimming has 2 athletes while Handball has 1 athlete."
    },
    {
        "title": "Average Performance Score",
        "content": "The average Performance Score across all athletes is 59."
    }
]
    prompt=recommender_prompt(df,insight_cards)
    structured_llm = llm.with_structured_output(recommender_schema)
    response = structured_llm.invoke(prompt)
    print(response)

    return  {"recommendation": response}


    
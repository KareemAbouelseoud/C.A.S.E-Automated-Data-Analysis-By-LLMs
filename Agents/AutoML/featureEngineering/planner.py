from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from dotenv import load_dotenv
import json
from pydantic import BaseModel, Field
from typing import List
load_dotenv()


CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

class Feature_Engineered(BaseModel):
    feature_name: str = Field(description="The name of the feature engineered")
    feature_logic: str = Field(description="The logic behind how to create the feature, not the code")
    reasoning: str = Field(description="Reasoning for engineering the feature")

class Feature_List(BaseModel):
    """Main structured output model"""
    features: List[Feature_Engineered] = Field(
        description="List of Features Engineered")


system_prompt = hub.pull("automl-feature-engineering-planner").messages[0].prompt.template
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

async def planner_node(state):
    print("Planning Feature Engineering",flush=True)
    data_report=state['data_report']
    messages=[
            {"role": "system", "content":system_prompt },
            {"role": "user", "content": f"Data Report:\n {data_report}\n Training Features: {state['X_columns']}\n Target Feature: {state['y_column']}\n Problem Type: {state['problem_type']}"},
        ]
    response= await llm.with_structured_output(Feature_List).ainvoke(messages)

    return {
        'feature_engineering_logic': json.dumps(response.model_dump()),
    }
from pydantic import BaseModel, Field
from typing import List,Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from API.Requests import projectRequests

class Feature(BaseModel):
    feature_name: str = Field(description="Name of the feature")
    feature_type: Literal['str','int','float','bool','datetime'] = Field(description="Type of the feature")
    streamlit_input: Literal['number_input', 'text_input', 'text_area', 'slider', 'checkbox', 'selectbox', 'radio', 'multiselect','time_input','date_input']
    streamlit_parameters: str = Field(description="Parameters to pass for the streamlit input type in JSON format",default="{}")


class Feature_list(BaseModel):
    """Main structured output model"""
    features: List[Feature] = Field(
        description="List of Features")

CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'],temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("automl-deployer").messages[0].content
async def deployer_node(data_report,X_columns):
    print(f"Deployer Started")
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": 
                f"\n\nData Report: {data_report}\nX_columns: {X_columns}\n"
                "Please provide the features for the deployment form. Make sure to include parameters for each feature."

        }
    ]
    response = await llm.with_structured_output(Feature_list).ainvoke(messages)
    return response.features

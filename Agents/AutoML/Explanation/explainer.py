from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
load_dotenv()
from pydantic import BaseModel, Field

system_prompt = hub.pull("automl-explainer").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

class Explainer(BaseModel):
    """ A Pydantic model to structure the output of the language model. """
    formatted_response: str = Field(description="The formatted response that will be displayed to the user")


async def explainer_node(input_data=None):
    if input_data is None:
        return None
    if isinstance(input_data, list):
        input_data=input_data[-1]
    llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'],max_tokens=4096)
    messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': input_data.content}]
    print("Explainer Messages: ",messages)
    response= await llm.with_structured_output(Explainer).ainvoke(messages)

    return response.formatted_response
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
import sys
import os
import json
from typing import Literal
import re
import httpx
from bs4 import BeautifulSoup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
load_dotenv()

system_prompt = hub.pull("automl-tuner").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

class Splitter(BaseModel):
    """ A Pydantic model to structure the output of the language model. """
    n_iter: int = Field(description="Number of iterations for the hyperparameter search this is A MUST FOR ATHENA MODE ",default=None)
    params_distribution: str = Field(description="The grid that will be searched for the best hyperparameters (in JSON string format. None should be null. There is no such parameter as 'none')")

async def fetch_url_content(url: str) -> str:
    """Fetches and returns text content from a URL asynchronously."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            content= soup.get_text(separator='')
            left_index = f"class sklearn."
            right_index = "Notes"
            
            # Split content by the left and right indexes
            if left_index in content and right_index in content:
                start = content.find(left_index)
                end = content.find(right_index, start)
                if end > start:
                    extracted_content = content[start:end]
                    return extracted_content
                else:
                    print(f"Could not extract content between {left_index} and {right_index}")
            else:
                print(f"Indexes not found in content")
    except Exception as e:
        print(f"Failed to fetch content from {url}: {e}")
        return ""
        
async def tuner_node(state):
    data_report=state['data_report']
    print("Tuner Node",flush=True)
    if 'models_completed' not in state:
        models_completed=0
    else:
        models_completed=state['models_completed']
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
    
    message_content=f"MODE: {state['mode']}\nTrain Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']} \n Problem Type: {state['problem_type']} \n"
    
    if state['problem_type']=="classification":
        message_content+=f"\n Stratified {state['stratify']}"
    
    if state['cross_validation']:
        message_content+=f"\n Cross Validation: {state['n_splits']} splits"
    else:
        message_content+=f"\n Val Size: {state['val_size']}"
    

    message_content+= f"THIS IS THE MODEL (IMPORTANT): {state['models'][models_completed]['model']}"
    # Fetch additional knowledge from a provided URL
    url = state['models'][models_completed].get('reference_url', None)
    if url:
        web_content = await fetch_url_content(url)
        if web_content:
            print(f"Additional Reference Data from {url}:\n{web_content}",flush=True)
            message_content += f"\n\nAdditional Reference Data from {url}:\n{web_content}"
    
    
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" },
        {"role": "user", "content":message_content},
    ]

    response= await llm.with_structured_output(Splitter).ainvoke(messages)
    try:
        params_string=response.params_distribution.replace("None","null")
        params_string=params_string.replace('True','true')
        params_string=params_string.replace('False','false')
        # Handle tuples specially - convert them to lists
        # This regex matches patterns like (64,) or (128, 64)
        # Convert tuple representations like (64,) to JSON array format
        params_string = re.sub(r'\((\d+),\)', r'[\1]', params_string)
        # Convert tuple representations like (128, 64) to JSON array format
        params_string = re.sub(r'\((\d+(?:,\s*\d+)+)\)', r'[\1]', params_string)
        
        print(params_string)
        params=json.loads(params_string)
    except Exception as e:
        print("Error in parsing the params")
        raise e
        params=None

    return {
        'n_iter': response.n_iter,
        'params_distribution': params,
        'models_completed': models_completed
    }

def tuner_decide_to_finish(state)-> Literal['model_tuner_node','model_trainer_node']:
    if state['params_distribution'] is None:
        return 'model_tuner_node'
    else:
        return 'model_trainer_node'
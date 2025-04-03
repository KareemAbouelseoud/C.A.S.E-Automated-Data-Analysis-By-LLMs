from pydantic import BaseModel,Field
from typing import Annotated
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
from langchain_core.tools import InjectedToolArg,tool
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
@tool
async def tuner_node(state: Annotated[dict,InjectedToolArg] = None,
                     model_names: Annotated[list[str],"This is the list of models that you want to tune. The naming must be identical to how model_selection has given."]=None,
                     task: Annotated[str,"This is the task that the supervisor node should assign or give. It is completely optional, You can write what are your preferences or comments"]=None):
    data_report=state['data_report']
    print("Tuner Node",flush=True)
    model_dict=state.get('models', {})
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
    messages=[{"role": "system", "content":system_prompt}]+state.get('tuning_messages', [])
    output={}
    for model in model_names:
        last_message=""
        if state.get("evaluation_metrics", None):
            last_message+=f"Here are the evaluation metrics for your previous steps: {state['evaluation_metrics']}\n\n Attempt to Analyze and Improve, if possible, if not return the same values.\n\n"

        if task:
            last_message+=f"Here are the instructions for you given by the supervisor, if it doesn't apply to this model ignore it and move on: {task}\n\n"

        last_message+=f"MODE: {state['mode']}\nData report: {data_report}\nTrain Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']} \n Problem Type: {state['problem_type']} \n"
    
        if state['problem_type']=="classification":
            last_message+=f"\n Stratified {state['stratify']}"
        
        if state['cross_validation']:
            last_message+=f"\n Cross Validation: {state['n_splits']} splits"
        

        last_message+= f"THIS IS THE MODEL (IMPORTANT): {model} \n\n"
        # Fetch additional knowledge from a provided URL
        url = state.get('models',{}).get(model,{}).get('reference_url', None)
        reference=''
        if url:
            web_content = await fetch_url_content(url)
            if web_content:
                print(f"Additional Reference Data from {url}:\n{web_content}",flush=True)
                reference += f"\n\nAdditional Reference Data from {url}:\n{web_content}"
    


        response= await llm.with_structured_output(Splitter).ainvoke(messages+[{"role": "user", "content": last_message+reference}])
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
            
            params=json.loads(params_string)
            model_dict[model]['params_distribution']=params
            output[model] = {
                "params_distribution": params,
            }
            if response.n_iter:
                model_dict[model]['n_iter']=response.n_iter
                output[model]['n_iter']=response.n_iter
            
        except Exception as e:
            print(f"Error in parsing the params: {e}")
            output[model] = f"Error has occured: {e}"

    new_state={
        "models": model_dict,
        "tuning_messages":[{"role": "user", "content": last_message},{"role": "assistant", "content": f"Here is the output: {output}"}]
    }
    return [f"Here is the output: {output} ",new_state]

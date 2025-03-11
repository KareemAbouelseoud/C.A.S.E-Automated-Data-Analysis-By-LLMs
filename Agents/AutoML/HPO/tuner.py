from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
import sys
import os
import json
from typing import Literal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
load_dotenv()

system_prompt = hub.pull("automl-tuner").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

class Splitter(BaseModel):
    """ A Pydantic model to structure the output of the language model. """
    n_iter: int = Field(description="Number of iterations for the hyperparameter search")
    params_distribution: str = Field(description="The grid that will be searched for the best hyperparameters (in JSON string format. None should be null. There is no such parameter as 'none')")

async def tuner_node(state):
    data_report=state['data_report']
    print("Tuner Node")
    if 'models_completed' not in state:
        models_completed=0
    else:
        models_completed=state['models_completed']
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
    
    message_content=f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']} \n Problem Type: {state['problem_type']} \n"
    
    if state['problem_type']=="classification":
        message_content+=f"\n Stratified {state['stratify']}"
    
    if state['cross_validation']:
        message_content+=f"\n Cross Validation: {state['n_splits']} splits"
    else:
        message_content+=f"\n Val Size: {state['val_size']}"
    

    message_content+= f"THIS IS THE MODEL (IMPORTANT): {state['models'][models_completed]['model']}"


    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" },
        {"role": "user", "content":message_content},
    ]

    response= await llm.with_structured_output(Splitter).ainvoke(messages)
    try:
        params_string=response.params_distribution.replace("None","null")
        params_string=params_string.replace('True','true')
        params_string=params_string.replace('False','false')
        print(params_string)
        params=json.loads(params_string)
    except:
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
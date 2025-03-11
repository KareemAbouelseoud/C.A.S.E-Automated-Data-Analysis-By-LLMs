from typing import Literal
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from API.Requests import projectRequests
load_dotenv()
client = Client(api_key=os.getenv("LANGCHAIN_API_KEY"))

system_prompt = client.pull_prompt("automl-splitter").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

class Splitter(BaseModel):
    """ A Pydantic model to structure the output of the language model. """
    test_size: float = Field(description="Test size for splitting the data")
    shuffle: bool = Field(description="Whether to shuffle the data before splitting")
    stratify: bool = Field(description="Whether to stratify the data before splitting")
    X_columns: list[str] = Field(description="The columns to use as features for training the model, Remove any columns that are not needed such as ID columns")
    cross_validation: bool = Field(description="Whether to use cross validation.")
    n_splits: int = Field(description="Number of splits for cross validation. If cross_validation is False, this value should be 1")
    val_size: float = Field(description="Validation size for splitting the data. If cross_validation is True, this value should be 0")
    logic: str = Field(description="The logic used to split the data and selection of features")
    problem_type: Literal["classification", "regression"] = Field(description="The problem type of the data")

async def splitter_node(state):
    print("Beginning Splitter Node")
    
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
    data_report=state['data_report']
    df = await projectRequests.get_dataset(state['project_id'])


    if 'X_columns' not in state or state['X_columns'] is None:
        X_columns = df.columns.tolist()
    else:
        X_columns = state['X_columns']
    
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" },
        {"role": "user", "content": f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"},
    ]

    response = await llm.with_structured_output(Splitter).ainvoke(messages)


    new_X_columns = response.X_columns
    new_X_columns = list(set(new_X_columns).intersection(set(X_columns)))

    
    new_state={
        'problem_type':response.problem_type,
        'splitting_logic':response.logic,
        'X_columns':new_X_columns,
        'test_size':response.test_size,
        'shuffle':response.shuffle,
        'cross_validation':response.cross_validation,
    }
    if response.cross_validation:
        new_state['n_splits']=response.n_splits
    else:
        new_state['val_size']=response.val_size
    
    if response.problem_type == "classification":
        new_state['stratify']=response.stratify

    return new_state
    



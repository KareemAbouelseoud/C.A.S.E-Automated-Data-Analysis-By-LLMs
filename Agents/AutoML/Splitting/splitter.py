from typing import Literal,Annotated,Optional
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client
from dotenv import load_dotenv
import sys
import os
from langchain_core.tools import InjectedToolArg,tool
from sklearn.model_selection import train_test_split
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

@tool
async def splitter_node(state: Annotated[dict,InjectedToolArg] = None,
                        task: Optional[Annotated[str,"This is the task that the supervisor node should assign or give. It is completely optional, You can write what are your preferences or comments"]] = None) -> list[str]:
    """This agent is responsible for splitting the data into train val and test sets, usually this should be the first agent to call. 
    The agent is reponsible for these parameters, it will do the reasoning and return these values, you DO NOT NEED TO GIVE THEM TO THE AGENT:
    - test_size: Test size for splitting the data
    - shuffle: Whether to shuffle the data before splitting
    - stratify: Whether to stratify the data before splitting
    - X_columns: Initial and very simple feature selection, Remove any columns that are not needed such as ID columns
    - cross_validation: Whether to use cross validation or have a separate validation set.
    - n_splits: Number of splits for cross validation. If cross_validation is False, this value should be 1
    val_size: Validation size for splitting the data. If cross_validation is True, this value should be 0
    - logic: The logic used to split the data and selection of features
    - problem_type: The problem type of the data, either classification or regression.

    If enhancements or modifications are needed you can direct the agent to do so by writing them in the task parameter.
    """
    print("Beginning Splitter Node")
    
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
    data_report=state['data_report']


    if 'X_columns' not in state or state['X_columns'] is None:
        df = await projectRequests.get_dataset(state['project_id'])
        X_columns = df.columns.tolist()
    else:
        X_columns = state['X_columns']
    
    messages=[
        {"role": "system", "content":system_prompt },
    ]+state.get('splitting_messages', [])
    last_message=""
    if state.get('evaluation_metrics', None):
        last_message+=f"Here are the evaluation metrics for your previous steps: {state['evaluation_metrics']}\n\n Attempt to Analyze and Improve, if possible, if not return the same values.\n\n"
    
    if task:
        last_message+=f"Here are the instructions for you given by the supervisor: {task}\n\n"
    last_message+=f"Here is the lastest data available: Data Report:\n {data_report}\n\n Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"
    
    messages.append({"role": "user", "content":last_message })
    response = await llm.with_structured_output(Splitter).ainvoke(messages)
    new_messages=[messages[-1],
                  {"role": "assistant", "content": f"Here is the output: {response.model_dump_json()}"}]

    new_X_columns = response.X_columns
    new_X_columns = list(set(new_X_columns).intersection(set(X_columns)))

    
    new_state={}

    X=df[new_X_columns]
    y=df[state['y_column']]
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=state['test_size'],shuffle=state['shuffle'],stratify=y if response.stratify else None,random_state=42)
    
    if not response.cross_validation:
        X_train,X_val,y_train,y_val = train_test_split(X_train,y_train,test_size=response.val_size,shuffle=state['shuffle'],stratify=y_train if response.stratify else None,random_state=42)
        new_state['val_size']=response.val_size
        new_state['X_val']=X_val
        new_state['y_val']=y_val
    else:
        new_state['n_splits']=response.n_splits


    new_state={
        'problem_type':response.problem_type,
        'splitting_logic':[response.logic],
        'X_columns':new_X_columns,
        'test_size':response.test_size,
        'shuffle':response.shuffle,
        'cross_validation':response.cross_validation,
        "splitting_messages":new_messages,
        'X_train':X_train,
        'y_train':y_train,
        'X_test':X_test,
        'y_test':y_test,
    }        
        
    if response.problem_type == "classification":
        new_state['stratify']=response.stratify

    return [f"""the splitting agent has decided that these are the suitable parameters: {response.model_dump_json()}.""",new_state]
    



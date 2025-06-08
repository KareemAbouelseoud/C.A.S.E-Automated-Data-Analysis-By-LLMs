import operator
from langchain_core.messages import AnyMessage
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict,Annotated,NotRequired,Optional,Any
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from preprocessingTools import tool_node
from planner import planner_node
from caller import caller_node,should_continue
from langchain_core.tools import tool,InjectedToolArg
import asyncio
import pandas as pd
from sklearn.utils import estimator_html_repr
load_dotenv()
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    data_report: NotRequired[str] # Data Report
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)
    planner_messages: Annotated[list[AnyMessage], operator.add] # Messages from the planner node
    preprocessing_messages: Annotated[list[AnyMessage], operator.add]
    preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    preprocessing_pipeline: NotRequired[Any] # Preprocessing Pipeline
    preprocessing_mode: NotRequired[str]
    task: NotRequired[str] # Task
    evaluation_metrics: NotRequired[Any] # Evaluation Metrics
    model_names: NotRequired[list] # Model Names

builder = StateGraph(State)

builder.add_node("planner_node", planner_node) 
builder.add_node("caller_node", caller_node) 
builder.add_node("tools",tool_node)

builder.add_edge(START, "planner_node")
builder.add_edge("planner_node", "caller_node")
builder.add_conditional_edges("caller_node", should_continue)
builder.add_edge('tools','caller_node')
graph = builder.compile()


@tool
async def preprocessing_node(
    state: Annotated[dict, InjectedToolArg] = None,
    # task: Optional[Annotated[str, "This is the task that the supervisor node should assign or give. It is completely optional, You can write what are your preferences or comments"]] = None,
    mode:Annotated[str, "This is the mode of the preprocessing. It can be 'X' or 'Y'."] = None,
) -> State:
    """
    This agent is responsible for preprocessing the data. It handles, no need to tell the agent what to do. It will automatically identify the data types and handle them accordingly, but you can give it instructions.:
    handle_outliers we identify either by iqr or z score then handle them by imputing mean, median or winsorizing or removing them.
    parse_datetime to different columns
    handle_null_values by removing them or replacing them with the mean median or mode, or by custom value
    remove_duplicates
    encode_categorical_feature by one hot encoding or label encoding
    normalize_continous_feature by min max scaling or standard scaler or robust scaler

    You can add these steps, change them or remove them simply by addressing it in the task parameter. HOWEVER THE MAIN FUNCTIONALITY OF THE AGENT IS TO IDENTIFY THE DATA TYPES AND HANDLE THEM ACCORDINGLY WITHOUT WRITING ANYTHING.
    If enhancements are needed you can direct the agent to do so by writing them in the task parameter.
    """
    old_state=state.copy()
    # state['task']=task
    state['preprocessing_mode']=mode
    if mode=='X' and state.get('X_preprocessing_messages', None):
        state['planner_messages']=state['X_preprocessing_messages']
    elif mode=='Y' and state.get('Y_preprocessing_messages', None):
        state['planner_messages']=state['Y_preprocessing_messages']

    if mode=='X' and state.get('X_preprocessing_pipeline', None):
        state['preprocessing_pipeline']=state['X_preprocessing_pipeline']
    elif mode=='Y' and state.get('Y_preprocessing_pipeline', None):
        state['preprocessing_pipeline']=state['Y_preprocessing_pipeline']

    models=state.get('models', None)
    if models:
        state['model_names']=list(models.keys())
    #TODO SEE HOW TO INTEGRATE EVALUATION METRICS TO ENHANCE THE AGENT
    new_state=await graph.ainvoke(state)
    preprocessor=new_state.get('preprocessing_pipeline', None)
    if preprocessor:
        for transformer in preprocessor.transformers[:]:
            if not transformer[1].steps:
                preprocessor.transformers.remove(transformer)
            
        returned_state={}
        if mode=='X':
            print(preprocessor)
            returned_state['X_preprocessing_messages']=old_state.get('X_preprocessing_messages', [])+new_state['planner_messages']
            returned_state['X_preprocessing_logic']=old_state.get('X_preprocessing_logic', [])+[new_state['preprocessing_logic']]
            preprocess_without_cross_validation(state['X_train'],preprocessor)[0].to_csv(f"X_preprocessing_pipeline_{state['project_id']}.csv",index=False)
            returned_state['X_preprocessing_pipeline']=preprocessor
            returned_state['X_pipeline_html']=estimator_html_repr(preprocessor)
        else:
            returned_state['Y_preprocessing_messages']=old_state.get('Y_preprocessing_messages', [])+new_state['planner_messages']
            returned_state['Y_preprocessing_logic']=old_state.get('Y_preprocessing_logic', [])+[new_state['preprocessing_logic']]
            returned_state['Y_preprocessing_pipeline']=preprocessor
            returned_state['Y_pipeline_html']=estimator_html_repr(preprocessor)
            preprocess_without_cross_validation(state['y_train'],preprocessor)
        completed=state.get('completed',{})
        completed['preprocessor']=True
        returned_state['completed']=completed
        return [f"Preprocessor has completed the task. here is the the new pipeline {preprocessor}.",returned_state]
    else:
        return [f"Preprocessor has not decided no preprocessing is needed for the task.",old_state]

def preprocess_without_cross_validation(data,preprocessor,final_imputer=None,Dropper=None,fit=True):
    preprocessor.transformers = [t for t in preprocessor.transformers if t is not None]

    # Remove duplicates from transformers
    if fit:
        seen_transformers = set()
        unique_transformers = []
        for transformer in preprocessor.transformers:
            if transformer[0]=='Final Imputer':
                final_imputer=transformer[1]
                continue
            if not hasattr(transformer[1], 'steps') or not transformer[1].steps:
                    continue
            if transformer[0] not in seen_transformers:
                unique_transformers.append(transformer)
                seen_transformers.add(transformer[0])
        preprocessor.transformers = unique_transformers
    
    # Separate the Dropper transformer if it exists
    if Dropper:
        temp_data = Dropper[1].fit_transform(data) if fit else Dropper[1].transform(data)
    else:
        if preprocessor.transformers and preprocessor.transformers[0][0]=='Drop':
            Dropper=preprocessor.transformers.pop(0)
            if Dropper[1].steps:
                temp_data=Dropper[1].fit_transform(data) if fit else Dropper[1].transform(data)
            else:
                temp_data=data
        else:
            temp_data=data

    # if there are any transformers left, apply them
    if preprocessor.transformers:
        temp_data=preprocessor.fit_transform(temp_data) if fit else preprocessor.transform(temp_data)

        # temp_data is a numpy array, so we need to convert it to a DataFrame and assign column names
        columns=preprocessor.get_feature_names_out()
        # The names of the columns are in the format 'step__column_name', so we need to remove the 'step__' part
        columns=[column.split('__',1)[1] if '__' in column else column for column in columns]
        temp_data=pd.DataFrame(temp_data,columns=columns)
    
    # Last Defence for any missing values
    if final_imputer:
        temp_data=final_imputer.fit_transform(temp_data) if fit else final_imputer.transform(temp_data)
        temp_data=pd.DataFrame(temp_data,columns=columns)
    else:
        temp_data=temp_data.dropna()
    
    return temp_data,final_imputer,Dropper,preprocessor 
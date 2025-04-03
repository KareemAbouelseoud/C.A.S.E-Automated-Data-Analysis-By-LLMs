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
    task: Optional[Annotated[str, "This is the task that the supervisor node should assign or give. It is completely optional, You can write what are your preferences or comments"]] = None,
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
    state['task']=task
    state['preprocessing_mode']=mode
    state['planner_messages']=state.get('X_preprocessing_messages', None) if mode=='X' else state.get('Y_preprocessing_messages', None)
    state['preprocessing_pipeline']=state.get('X_pipeline', None) if mode=='X' else state.get('Y_pipeline', None)
    models=state.get('models', None)
    if models:
        state['model_names']=list(models.keys())
    #TODO SEE HOW TO INTEGRATE EVALUATION METRICS TO ENHANCE THE AGENT
    new_state=graph.ainvoke(state)

    returned_state={}
    if mode=='X':
        returned_state['X_preprocessing_messages']=new_state['planner_messaages']
        returned_state['X_preprocessing_logic']=[new_state['preprocessing_logic']]
        returned_state['X_pipeline']=new_state['preprocessing_pipeline']
    else:
        returned_state['Y_preprocessing_messages']=new_state['planner_messages']
        returned_state['Y_preprocessing_logic']=[new_state['preprocessing_logic']]
        returned_state['Y_pipeline']=new_state['preprocessing_pipeline']

    # Apply Preprocessing Pipeline to the Data
    preprocessor_name='X_pipeline' if mode=='X' else 'Y_pipeline'
    train="X_train" if mode=='X' else 'y_train'
    test="X_test" if mode=='X' else 'y_test'
    val="X_val" if mode=='X' else 'y_val'
    
    preprocessor=returned_state[preprocessor_name]
    returned_state[train]=preprocessor.fit_transform(state[train])

    tasks = [asyncio.to_thread(preprocessor.transform, state[test])]
    if state.get(val, None):
        tasks.append(asyncio.to_thread(preprocessor.transform, state[val]))

    results = await asyncio.gather(*tasks)

    returned_state[test] = results[0]
    if state.get(val, None):
        returned_state[val] = results[1]

    return [f'Preprocessor has completed the task. here is the the new pipeline {new_state['preprocessing_pipeline']}.',returned_state]
from langchain_openai import ChatOpenAI
import dotenv
import os
import sys
from typing import  TypedDict, NotRequired,Annotated,Any
from langgraph.graph import StateGraph, START
from langchain_core.messages import AnyMessage
import operator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..',)))
from langgraph.checkpoint.memory import MemorySaver
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
checkpointer = MemorySaver()


dotenv.load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")


class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    data_report: NotRequired[str] # Data Report
    mode: str # Mode Selected by the User
    user_preferences: NotRequired[str] # User Preferences
    
    #Data Names
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)
    problem_type: NotRequired[str] # Problem Type Identified by the LLM
    X_train: NotRequired[Any] # X Train
    #Splitting
    splitting_logic: NotRequired[str] # Splitting Steps Documented for the User and rest of Agents
    test_size: NotRequired[float] # Test Size
    test_count: NotRequired[int] # Test Count
    shuffle: NotRequired[bool] # Shuffle
    stratify: NotRequired[bool] # Stratify
    cross_validation: NotRequired[bool] # Cross Validation
    
    n_splits: NotRequired[int] # Number of Splits
    val_size: NotRequired[float] # Validation Size
    val_count: NotRequired[int] # Validation Count

    train_count: NotRequired[int] # Train Count
    
    splitting_messages:Annotated[list[AnyMessage], operator.add]

    #Tuning
    n_iter: NotRequired[int] # Number of Iterations
    params_distribution: NotRequired[dict] # Parameters Distribution
    tuning_messages: Annotated[list[AnyMessage], operator.add]

    #Preprocessing Pipeline
    X_preprocessing_logic: NotRequired[list[str]]  # Preprocessing Steps Documented for the User and rest of Agents
    Y_preprocessing_logic: NotRequired[list[str]]  # Preprocessing Steps Documented for the User and rest of Agents
    X_preprocessing_pipeline: NotRequired[Any] # X Preprocessing Pipeline
    preprocessing_messages: Annotated[list[AnyMessage], operator.add] # Preprocessing Messages for X and Y

    X_pipeline_html: NotRequired[str] # X Pipeline HTML
    Y_pipeline_html: NotRequired[str] # Y Pipeline HTML
    
    #Model
    models: NotRequired[list] # Model Names Selected by LLM
    models_completed: NotRequired[int] # Number of Models Completed
    model_selection_messages: Annotated[list[AnyMessage], operator.add] # Model Selection Messages

    #Evaluation
    evaluation_reports: NotRequired[list] # Evaluation Reports

    #supervisor
    messages: Annotated[list[AnyMessage], operator.add]
    completed: NotRequired[dict] # Completed
    steps: NotRequired[int] = 0


async def supervisor_node(state):
    print(state.get('project_id', None))
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('encoder', OneHotEncoder()),
    ])
    return {"X_preprocessing_pipeline": pipeline,}

builder = StateGraph(State)

builder.add_node("supervisor_node", supervisor_node)

builder.add_edge(START, "supervisor_node")
graph = builder.compile()

import asyncio
async def main():
    result = await graph.ainvoke({'project_id':"67c1ba76e833b024ca9cb615","hello":'world'})
    print(result)
asyncio.run(main())
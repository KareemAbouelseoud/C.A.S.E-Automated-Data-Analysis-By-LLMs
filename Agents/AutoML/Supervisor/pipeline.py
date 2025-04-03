from typing import TypedDict, NotRequired,Annotated,Any
from langgraph.graph import StateGraph, START
from .supervisor import supervisor_node, should_continue
from .supervisorTools import tool_node
from langchain_core.messages import AnyMessage
import operator


CONFIGURATIONS= {
    'recursion_limit': 100,
}
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

    #Splitting
    splitting_logic: Annotated[NotRequired[list[str]],operator.add]=None # Splitting Steps Documented for the User and rest of Agents
    test_size: NotRequired[float] # Test Size
    test_count: NotRequired[int] # Test Count
    shuffle: NotRequired[bool] # Shuffle
    stratify: NotRequired[bool] # Stratify
    cross_validation: NotRequired[bool] # Cross Validation
    
    n_splits: NotRequired[int] # Number of Splits
    val_size: NotRequired[float] # Validation Size
    val_count: NotRequired[int] # Validation Count
    
    X_train: NotRequired[Any] # X Train
    y_train: NotRequired[Any] # Y Train
    X_test: NotRequired[Any] # X Test
    y_test: NotRequired[Any] # Y Test
    X_val: NotRequired[Any] # X Validation
    y_val: NotRequired[Any] # Y Validation

    train_count: NotRequired[int] # Train Count
    
    splitting_messages:Annotated[list[AnyMessage], operator.add] # conversation between supervisor and splitter

    #Tuning
    n_iter: NotRequired[int] # Number of Iterations
    params_distribution: NotRequired[dict] # Parameters Distribution
    tuning_messages: Annotated[list[AnyMessage], operator.add]

    #Preprocessing Pipeline
    X_preprocessing_logic: Annotated[NotRequired[list[str]],operator.add]=None # Preprocessing Steps Documented for the User and rest of Agents
    Y_preprocessing_logic: Annotated[NotRequired[list[str]],operator.add]=None  # Preprocessing Steps Documented for the User and rest of Agents
    X_pipeline: NotRequired[Any] # Preprocessing Pipeline for X
    Y_pipeline: NotRequired[Any] # Preprocessing Pipeline for Y

    X_preprocessing_messages: list[AnyMessage] # Conversation between supervisor and preprocessing planner
    Y_preprocessing_messages: list[AnyMessage] # Conversation between supervisor and preprocessing planner

    X_pipeline_html: NotRequired[str] # X Pipeline HTML
    Y_pipeline_html: NotRequired[str] # Y Pipeline HTML
    
    #Model
    models: NotRequired[dict] # Model Names Selected by LLM
    models_completed: NotRequired[int] # Number of Models Completed
    model_selection_messages: Annotated[list[AnyMessage], operator.add] # Model Selection Messages

    #Evaluation
    evaluation_reports: NotRequired[list] # Evaluation Reports

    #supervisor
    messages: Annotated[list[AnyMessage], operator.add]
    completed: NotRequired[dict] # Completed
    steps: NotRequired[int] = 0



builder = StateGraph(State)

builder.add_node("supervisor_node", supervisor_node)
builder.add_node("tools",tool_node)

builder.add_edge(START, "supervisor_node")
builder.add_conditional_edges('supervisor_node', should_continue)
builder.add_edge('tools', 'supervisor_node')
graph = builder.compile()
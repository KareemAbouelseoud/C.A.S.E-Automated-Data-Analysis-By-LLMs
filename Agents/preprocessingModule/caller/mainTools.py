from io import StringIO
from langchain.tools import tool
import pandas as pd
import numpy as np
from typing import Literal, Annotated
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolArg
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Global variable for the preprocessed dataframe
global_df = None

"""
mainTools.py

This module defines the main tools for the preprocessing module.
The tools are designed to handle missing values, remove outliers, and change the data type of a column.

Dependencies:
- langchain_core
- pandas
- numpy
- langchain_core.messages
- langchain_core.tools
- API.Requests.projectRequests

Functions:
- handle_missing_values: Handle missing values in a specified column using the given strategy.
- remove_outliers: Remove outliers from a column using the specified method.
- change_column_type: Change the data type of a column.

Variables:
- tools: A list of tools defined in the module.
- tool_node: A function that invokes the tools based on the state messages.
- tool_brancher: A function that branches the state messages based on the tool call.
"""

# @tool
# async def handle_missing_values(column: str, strategy: str) -> pd.DataFrame:
#     """Handle missing values in a specified column using the given strategy.
    
#     Args:
#         column: The column name to process
#         strategy: The strategy to use ('mean', 'median', 'mode', 'drop')
    
#     Returns:
#         pd.DataFrame: The preprocessed DataFrame
#     """
#     global global_df
#     preprocessed_df = global_df.copy()
#     try:
#         print(f"running handle missing values tool on column: {column} with strategy: {strategy}")
#         if global_df is None:
#             raise ValueError("No DataFrame loaded. Please load a DataFrame first.")
            
#         if column not in global_df.columns:
#             raise ValueError(f"Column '{column}' not found in dataset")
        
#         if strategy != 'drop':
#             if not pd.api.types.is_numeric_dtype(global_df[column]):
#                 raise TypeError(f"Column '{column}' must be numeric for {strategy} strategy")   
#         if strategy == 'mean':
#             preprocessed_df[column] = global_df[column].fillna(global_df[column].mean())
#         elif strategy == 'median':
#             preprocessed_df[column] = global_df[column].fillna(global_df[column].median())
#         elif strategy == 'mode':
#             preprocessed_df[column] = global_df[column].fillna(global_df[column].mode()[0])
#         elif strategy == 'drop':
#             preprocessed_df = global_df.dropna(subset=[column])
#         else:
#             raise ValueError(f"Invalid strategy: {strategy}. Must be one of: mean, median, mode, drop")
            
#         return {"status" : "success", "preprocessed_dataframe" : preprocessed_df}
        
#     except Exception as e:
#         print(f"Tool-Error handling missing values in column {column} with strategy {strategy},: {str(e)}")
#         return {"status" : "error", "error" : str(e)}

@tool
async def remove_outliers(column: str, method: str, threshold: float = 3.0) -> pd.DataFrame:
    """Remove outliers from a column using the specified method.
    
    Args:
        column: The column name to process
        method: The method to use ('zscore', 'iqr')
        threshold: The threshold for outlier detection
    
    Returns:
        pd.DataFrame: The preprocessed DataFrame
    """
    global global_df
    preprocessed_df = global_df.copy()
    try:
        if global_df is None:
            raise ValueError("No DataFrame loaded. Please load a DataFrame first.")
            
        if column not in global_df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
            
        if not pd.api.types.is_numeric_dtype(global_df[column]):
            raise TypeError(f"Column '{column}' must be numeric for outlier detection")
            
        if method == 'zscore':
            z_scores = np.abs((global_df[column] - global_df[column].mean()) / global_df[column].std())
            global_df = global_df[z_scores < threshold]
        elif method == 'iqr':
            Q1 = global_df[column].quantile(0.25)
            Q3 = global_df[column].quantile(0.75)
            IQR = Q3 - Q1
            preprocessed_df = global_df[~((global_df[column] < (Q1 - 1.5 * IQR)) | (global_df[column] > (Q3 + 1.5 * IQR)))]
        else:
            raise ValueError(f"Invalid method: {method}. Must be one of: zscore, iqr")
            
        return {"status" : "success", "preprocessed_dataframe" : preprocessed_df}
        
    except Exception as e:
        print(f"Tool-Error removing outliers from column {column}: {str(e)}")
        return {"status" : "error", "error" : str(e)}

@tool
async def change_column_type(column: str, target_type: str, format: str = None) -> pd.DataFrame:
    """Change the data type of a column.
    
    Args:
        column: The column name to change type
        target_type: The target data type ('datetime', 'int', 'float', 'string')
        format: Format string for datetime conversion (e.g. '%Y-%m-%d')
    
    Returns:
        pd.DataFrame: The DataFrame with changed column type
    """
    global global_df
    preprocessed_df = global_df.copy()
    try:
        if global_df is None:
            raise ValueError("No DataFrame loaded. Please load a DataFrame first.")
            
        if column not in global_df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
            
        if target_type == 'datetime':
            preprocessed_df[column] = pd.to_datetime(global_df[column], format=format)
        elif target_type == 'int':
            preprocessed_df[column] = global_df[column].astype(int)
        elif target_type == 'float':
            preprocessed_df[column] = global_df[column].astype(float)
        elif target_type == 'string':
            preprocessed_df[column] = global_df[column].astype(str)
        else:
            raise ValueError(f"Unsupported target type: {target_type}. Must be one of: datetime, int, float, string")
            
        return {"status" : "success", "preprocessed_dataframe" : preprocessed_df}
        
    except Exception as e:
        print(f"Tool-Error converting column {column} to {target_type}: {str(e)}")
        return {"status" : "error", "error" : str(e)}

tools = [remove_outliers, change_column_type]

async def tool_node(state)->Literal["caller", "__end__"]:
    """
    Process tool calls from the last message.
    
    Args:
        state (dict): The current state containing:
            - messages: List of messages in the conversation
            - dataframe: The input DataFrame
            - preprocessing_tasks: The task to process
            - target_column: The column to process
            - strategy: The strategy to use
    
    Returns:
        dict: Updated state with:
            - next: Next node to execute
            - preprocessed_dataframe: The processed DataFrame
            - messages: Updated message history
            - error: Error status
    """
    global global_df
    tools_by_name = {tool.name: tool for tool in tools}
    
    # Initialize state
    if 'iterations' not in state or state['iterations'] is None:
        state['iterations'] = 0
    retries = state['iterations'] + 1
    
    if retries > 3:
        return {"next": "__end__", "error": "Max tool retries exceeded"}
    
    # Get task details from state
    task = state.get("preprocessing_tasks")
    column = state.get("target_column")
    strategy = state.get("strategy")
    
    if not all([task, column, strategy]):
        raise ValueError("Missing required fields in state: preprocessing_tasks, target_column, or strategy")
    
    global_df = pd.read_json(StringIO(state['dataframe'])) if isinstance(state['dataframe'], str) else state['dataframe']
    
    try:
        # Execute the tool based on the task
        tool_name = task
        tool_args = {
            "column": column,
            "method": strategy,
            "target_type": strategy 
        }
        
        # Remove None values from args
        tool_args = {k: v for k, v in tool_args.items() if v is not None}
        
        print(f"---TOOL CALL ARGS: {tool_args}---")
        tool_result = await tools_by_name[tool_name].ainvoke(tool_args)
        print(f"---TOOL RESULT: {tool_result}---")
        
        # Update the global dataframe with the result
        if isinstance(tool_result, dict) and 'preprocessed_dataframe' in tool_result:
            global_df = tool_result['preprocessed_dataframe']
        
        # Return success state
        return {
            "next": "__end__",
            "iterations": 0,
            "preprocessed_dataframe": global_df.to_json(),
            "dataframe":state['dataframe'].to_json(),
            "error": "no",
            "messages": [{"role": "system", "content": "Tool execution successful"}]
        }
    
    except Exception as e:
        # Return the error if the tool call fails
        error_msg = f"{type(e).__name__}: {str(e)}"
        return {
            'next': 'caller',
            "dataframe":state['dataframe'],
            'messages': [{"role": "system", "content": f"Tool execution failed: {error_msg}"}],
            'iterations': retries,
            'error': 'yes'
        }

async def tool_brancher(state)-> Literal["caller", "__end__"]:
    return state['next']

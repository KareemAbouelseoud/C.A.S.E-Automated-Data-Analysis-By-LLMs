from langchain.tools import tool
import pandas as pd
import numpy as np
from typing import Literal, Annotated
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolArg
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API.Requests import projectRequests


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

@tool
async def handle_missing_values(column: str, strategy: str, project_id: Annotated[str,InjectedToolArg] = None) -> pd.DataFrame:
    """Handle missing values in a specified column using the given strategy.
    
    Args:
        column: The column name to process
        strategy: The strategy to use ('mean', 'median', 'mode', 'drop')
        project_id: The ID of the project to get data from
    
    Returns:
        pd.DataFrame: The preprocessed DataFrame
    """
    df = await projectRequests.get_dataset(project_id)
    
    try:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
            
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise TypeError(f"Column '{column}' must be numeric for {strategy} strategy")
            
        if strategy == 'mean':
            df[column] = df[column].fillna(df[column].mean())
        elif strategy == 'median':
            df[column] = df[column].fillna(df[column].median())
        elif strategy == 'mode':
            df[column] = df[column].fillna(df[column].mode()[0])
        elif strategy == 'drop':
            df.dropna(subset=[column], inplace=True)
        else:
            raise ValueError(f"Invalid strategy: {strategy}. Must be one of: mean, median, mode, drop")
            
        return df
        
    except Exception as e:
        raise ValueError(f"Error handling missing values in column {column}: {str(e)}")

@tool
async def remove_outliers(column: str, method: str, threshold: float = 3.0, project_id: Annotated[str,InjectedToolArg] = None) -> pd.DataFrame:
    """Remove outliers from a column using the specified method.
    
    Args:
        column: The column name to process
        method: The method to use ('zscore', 'iqr')
        threshold: The threshold for outlier detection
        project_id: The ID of the project to get data from
    
    Returns:
        pd.DataFrame: The preprocessed DataFrame
    """
    df = await projectRequests.get_dataset(project_id)
    
    try:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
            
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise TypeError(f"Column '{column}' must be numeric for outlier detection")
            
        if method == 'zscore':
            z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
            df = df[z_scores < threshold]
        elif method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            df = df[~((df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR)))]
        else:
            raise ValueError(f"Invalid method: {method}. Must be one of: zscore, iqr")
            
        return df
        
    except Exception as e:
        raise ValueError(f"Error removing outliers from column {column}: {str(e)}")

@tool
async def change_column_type(column: str, target_type: str, format: str = None, project_id: Annotated[str,InjectedToolArg] = None) -> pd.DataFrame:
    """Change the data type of a column.
    
    Args:
        column: The column name to change type
        target_type: The target data type ('datetime', 'int', 'float', 'string')
        format: Format string for datetime conversion (e.g. '%Y-%m-%d')
        project_id: The ID of the project to get data from
    
    Returns:
        pd.DataFrame: The DataFrame with changed column type
    """
    df = await projectRequests.get_dataset(project_id)
    
    try:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
            
        if target_type == 'datetime':
            df[column] = pd.to_datetime(df[column], format=format)
        elif target_type == 'int':
            df[column] = df[column].astype(int)
        elif target_type == 'float':
            df[column] = df[column].astype(float)
        elif target_type == 'string':
            df[column] = df[column].astype(str)
        else:
            raise ValueError(f"Unsupported target type: {target_type}. Must be one of: datetime, int, float, string")
    except Exception as e:
        raise ValueError(f"Error converting column {column} to {target_type}: {str(e)}")
            
    return df

tools = [handle_missing_values,remove_outliers, change_column_type]

async def tool_node(state)->Literal["caller", "__end__"]:
    tools_by_name = {tool.name: tool for tool in tools}
    
    messages = state["messages"]
    # get the last message of this state
    last_message = messages[-1]
    output_messages = []
    tool_outputs = []
    for tool_call in last_message.tool_calls:
        try:
            # Invoke the tool based on the tool call
            tool_call["args"]["project_id"] = state['project_id']
            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            tool_outputs.append(tool_result)
            return {"next": "__end__", 'preprocessing': tool_outputs}
        
        except Exception as e:
            # Return the error if the tool call fails
            output_messages.append(
                ToolMessage(
                    content="an error occurred while running the tool",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    additional_kwargs={"error": e},
                )
            )
            return {'next':'caller', 'messages':output_messages}

async def tool_brancher(state)-> Literal["caller", "__end__"]:
    return state['next']

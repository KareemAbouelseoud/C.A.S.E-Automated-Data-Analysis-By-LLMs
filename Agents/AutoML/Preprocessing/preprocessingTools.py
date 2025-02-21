import pandas as pd
from io import StringIO
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from typing import Annotated
import sys
import os
from pathlib import Path
import numpy as np
from sklearn.preprocessing import FunctionTransformer
from sklearn.impute import KNNImputer
from typing import Annotated, Optional, List
from Database import mainDatabase
from Backend.services.project_service import ProjectService
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
_project_service=ProjectService()
from typing import Annotated, Optional, List,Union
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from functools import partial
from helperFunctions import *
from Backend.services.project_service import ProjectService
_project_service=ProjectService()


@tool
async def encode_categorical_feature(
    column_name: Annotated[str, 'Column to encode.'],
    method: Annotated[str, 'Method: "onehot" or "label"'] = 'onehot',
    sparse: Annotated[bool, 'Whether to return a sparse matrix (for one-hot encoding ONLY).'] = True,
    project_id: str = None,
) -> tuple:
    """
    Encodes categorical features and returns a transformer to apply the same encoding to new data.
    """
    if method == 'onehot':
        encoder = OneHotEncoder(sparse_output=sparse, handle_unknown='ignore')
    elif method == 'label':
        encoder = LabelEncoder()
    else:
        raise ValueError(f"Unknown method: {method}")

    return ("encode_categorical_feature",encoder,[column_name])

@tool
async def normalize_continous_feature(
    column_name: Annotated[str, 'Column to normalize.'],
    method: Annotated[str, 'Method: "minmax" or "standard" or "log" or "robust"'] = 'minmax',
    project_id: str = None,
) -> tuple:
    """
    Normalizes continuous features and returns a transformer to apply the same normalization to new data.
    """
    if method == 'minmax':
        transformer = FunctionTransformer(minmax_transform)
    elif method == 'standard':
        transformer = FunctionTransformer(standard_transform)
    elif method == 'log':
        transformer = FunctionTransformer(log_transform)
    elif method == 'robust':
        transformer = FunctionTransformer(robust_transform)
    else:
        raise ValueError(f"Unknown method: {method}")

    return ("normalize_continous_feature",transformer,[column_name])

@tool
async def handle_outliers(
    column_name: Annotated[str, 'column name to be processed'],
    strategy: Annotated[str, "The strategy to handle outliers. Options: 'remove', 'impute_mean', 'impute_median','winsorize','knn"],
    project_id: str = None,
    n_neighbors: Annotated[Optional[int], "Number of neighbors for KNN imputation (if strategy is 'knn')."] = 5, 
    method: Annotated[str, 'Method: "zscore" or "iqr"'] = 'iqr',
    threshold: Annotated[float, 'Threshold for outlier detection.'] = 1.5
) -> tuple:
    """
    Detects outliers in the training data and returns a transformer to remove them.
    The transformer is configured with the training data's parameters (e.g., IQR bounds).

    Args:
        column_name: Name of the column to process.
        strategy: The strategy to handle outliers. Options: 'remove', 'impute_mean', 'impute_median', 'log_transform', 'winsorize', 'knn'.
        project_id: ID of the project to fetch the dataset.
        n_neighbors: Number of neighbors for KNN imputation (if strategy is 'knn').
        method: Outlier detection method ("zscore" or "iqr").
        threshold: Threshold for outlier detection.

    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer configured with the appropriate outlier detection method. This transformer can be applied to new data to remove outliers based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    data = await _project_service.fetch_dataset(project_id)

    try:
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
        if not pd.api.types.is_numeric_dtype(data[column_name]):
            raise ValueError(f"Column '{column_name}' is not numeric.")
        
        if strategy == 'remove':
            if method == 'iqr':
                transformer=FunctionTransformer(partial(remove_outlier_transform_by_iqr,threshold=threshold))

            elif method == 'zscore':
                transformer=FunctionTransformer(partial(remove_outlier_transform_by_zscore,threshold=threshold))
                
            else: 
                raise ValueError(f"Unknown method: {method}")
        
        
        elif strategy == 'impute_mean':
            if method == 'iqr':
                transformer=FunctionTransformer(partial(impute_mean_outlier_transform_by_iqr,threshold=threshold))

            elif method == 'zscore':
                transformer=FunctionTransformer(partial(impute_mean_outlier_transform_by_zscore,threshold=threshold))
            else: 
                raise ValueError(f"Unknown method: {method}")
                
        
        elif strategy == 'impute_median':
            if method == 'iqr':
                transformer=FunctionTransformer(partial(impute_median_outlier_transform_by_iqr,threshold=threshold))

            elif method == 'zscore':
                transformer=FunctionTransformer(partial(impute_median_outlier_transform_by_zscore,threshold=threshold))
            else: 
                raise ValueError(f"Unknown method: {method}")
                        
        
        elif strategy == 'winsorize':
            if method == "iqr":
                transformer = FunctionTransformer(partial(winsorize_outlier_transform_by_iqr, threshold=threshold))

            elif method == 'zscore':
                transformer = FunctionTransformer(partial(winsorize_outlier_transform_by_zscore, threshold=threshold))
            
            else: 
                raise ValueError(f"Unknown method: {method}")
            
                
        elif strategy == "knn":
            return KNNImputer(n_neighbors=n_neighbors)
    
        
        return ("handle_outliers",transformer,[column_name])
    
    except Exception as e:
        print(f"Error in handle_outliers: {e}") #can we make it more descriptive? LLM generated msg?

@tool
async def parse_datetime(
    column_name: Annotated[str, 'column name to be processed'],
    project_id: str = None,
) -> tuple:
    """
    Parses datetime columns and returns a transformer to apply the same parsing to new data.
    
    Args:
        column_name: Name of the column to process.
        project_id: ID of the project to fetch the dataset.

    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer. This transformer can be applied to new data to parse datetime strings based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    data = await _project_service.fetch_dataset(project_id)
    try:
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")

        return ("parse_datetime",FunctionTransformer(datetime_transform),[column_name])

    except Exception as e:
        print(f"Error in parse_datetime: {e}")

@tool
async def handle_null_values(
    column_name: Annotated[str, 'column name to be processed'],
    strategy: Annotated[str, "The strategy to handle null values. Options: 'drop', 'fill_value', 'fill_mean', 'knn"],
    project_id: str = None,
    value: Annotated[Optional[Union[float,str,int]], "The value to fill nulls with (if strategy is 'fill_value')."] = None,
    n_neighbors: Annotated[Optional[int], "Number of neighbors for KNN imputation (if strategy is 'knn')."] = 5,
) -> tuple:
    """
    Handle null values in a DataFrame using the specified strategy.
    
    Args:
        column_name: Name of the column to process.
        strategy : The strategy to handle null values. Options: 'drop', 'fill_value', 'fill_mean', 'knn'.
        project_id: ID of the project to fetch the dataset.
        value: The value to fill nulls with (if strategy is 'fill_value').
        n_neighbors: Number of neighbors for KNN imputation (if strategy is 'knn').
        

    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer configured with the appropriate outlier detection method. This transformer can be applied to new data to remove outliers based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    try:
        data =await _project_service.fetch_dataset(project_id)
        
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
         
        if strategy == "drop":
            transformer=FunctionTransformer(drop_transform)
        elif strategy == "fill_value":
            
            if value is None:
                raise ValueError("A value must be provided for the 'fill_value' strategy.")
            
            transformer = FunctionTransformer(partial(fill_value_transform, value=value))

        elif strategy == "fill_mean":
            transformer = FunctionTransformer(fill_mean_transform)

        elif strategy == "knn":
            return ("handle_null_values",KNNImputer(n_neighbors=n_neighbors),[column_name])
            
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    except Exception as e:
        raise e

    return ("handle_null_values", transformer, [column_name])

@tool
async def remove_duplicates(
    column_name: Annotated[str, 'column name to be processed'],
    strategy: Annotated[str, "The strategy to handle duplicates. Options: 'rows', 'columns'."],
    project_id: str = None,
    subset: Annotated[Optional[str], "List of columns to consider for row duplicates (if strategy is 'rows')."] = None,
    keep: Annotated[Optional[str], "Whether to keep the 'first', 'last', or False (if strategy is 'rows' or 'columns')."] = "first",
) -> tuple:
    """
    Remove duplicate rows or columns from a DataFrame using the specified strategy.

    Args:
        column_name: Name of the column to process.
        strategy : The strategy to handle duplicates. Options: 'rows', 'columns'.
        project_id: ID of the project to fetch the dataset.
        subset: List of columns to consider for row duplicates (if strategy is 'rows').
        keep: Whether to keep the 'first', 'last', or False (if strategy is 'rows' or 'columns').
        
    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer configured with the appropriate outlier detection method. This transformer can be applied to new data to remove outliers based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    try :
        data = await _project_service.fetch_dataset(project_id)
        
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
         
        if strategy == "rows":
            transformer=FunctionTransformer(partial(drop_rows_transform, subset=subset, keep=keep))
            
        elif strategy == "columns":
            transformer=FunctionTransformer(partial(drop_columns_transform, keep=keep))

        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    except:
        raise ValueError(f"Error in remove_duplicates")
    return ("remove_duplicates", transformer, [column_name])

tools=[
    handle_outliers,
    parse_datetime,
    handle_null_values,
    remove_duplicates,
    encode_categorical_feature,
    normalize_continous_feature
]

async def tool_node(state):
    print("Executing Tool Calls")
    tools_by_name = {tool.name: tool for tool in tools}
    messages = state["preprocessing_messages"]
    # get the last message of this state
    last_message = messages[-1]
    preprocessors = []
    output_messages = []
    for tool_call in last_message.tool_calls:
        try:
            # Invoke the tool based on the tool call
            tool_call["args"]["project_id"] = state["project_id"]
            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            preprocessors.append(tool_result)
            output_messages.append(
                ToolMessage(
                    content=f"Preprocessing step completed: {tool_call['name']} for column {tool_call['args']['column_name']} no need to call this function for this column again",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        except Exception as e:
            # Return the error if the tool call fails
            output_messages.append(
                ToolMessage(
                    content=f"an error occurred while running the tool: {str(e)}",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    status="error",
                )
            )
    ## TODO: Fetching & saving the pipeline to the database
    preprocessor=await _project_service.fetch_pipeline(state["project_id"])
    if preprocessor:
        preprocessor.transformers.extend(preprocessors)
    else:
        preprocessor=ColumnTransformer(transformers=preprocessors,remainder='passthrough')
    _project_service.save_pipeline(preprocessor,state["project_id"])
    
    return {'preprocessing_messages':output_messages}

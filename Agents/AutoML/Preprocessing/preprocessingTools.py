import pandas as pd
from io import StringIO
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from typing import Annotated
import sys
from pathlib import Path
import numpy as np
from sklearn.preprocessing import FunctionTransformer
from sklearn.impute import KNNImputer
from typing import Annotated, Optional, List
from Database import mainDatabase
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

@tool
async def encode_categorical_feature(
    column: Annotated[str, 'Column to encode.'],
    method: Annotated[str, 'Method: "onehot" or "label"'] = 'onehot',
    sparse: Annotated[bool, 'Whether to return a sparse matrix (for one-hot encoding ONLY).'] = True,
) -> tuple:
    """
    Encodes categorical features and returns a transformer to apply the same encoding to new data.
    """
    if method == 'onehot':
        encoder = OneHotEncoder(sparse=sparse, handle_unknown='ignore')
    elif method == 'label':
        encoder = LabelEncoder()
    else:
        raise ValueError(f"Unknown method: {method}")

    return ("encode_categorical_feature",encoder,[column])

@tool
async def normalize_continous_feature(
    column: Annotated[str, 'Column to normalize.'],
    method: Annotated[str, 'Method: "minmax" or "standard" or "log" or "robust"'] = 'minmax',
) -> tuple:
    """
    Normalizes continuous features and returns a transformer to apply the same normalization to new data.
    """
    if method == 'minmax':
        def minmax_transform(input_data):
            input_data = input_data.copy()
            return (input_data - input_data.min()) / (input_data.max() - input_data.min())
    elif method == 'standard':
        def standard_transform(input_data):
            input_data = input_data.copy()
            return (input_data - input_data.mean()) / input_data.std()
    elif method == 'log':
        def log_transform(input_data):
            input_data = input_data.copy()
            return np.log1p(input_data)
    elif method == 'robust':
        def robust_transform(input_data):
            input_data = input_data.copy()
            input_data = (input_data - input_data.median()) / (input_data.quantile(0.75) - input_data.quantile(0.25))
            return input_data
    else:
        raise ValueError(f"Unknown method: {method}")

    return ("normalize_continous_feature",FunctionTransformer(minmax_transform if method == 'minmax' else standard_transform if method == 'standard' else log_transform if method == 'log' else robust_transform),[column])

@tool
async def handle_outliers(
    column_name: Annotated[str, 'column name to be processed'],
    project_id: str = None,
    method: Annotated[str, 'Method: "zscore" or "iqr"'] = 'iqr',
    threshold: Annotated[float, 'Threshold for outlier detection.'] = 1.5
) -> tuple:
    """
    Detects outliers in the training data and returns a transformer to remove them.
    The transformer is configured with the training data's parameters (e.g., IQR bounds).

    Args:
        column_name: Name of the column to process.
        project_id: ID of the project to fetch the dataset.
        method: Outlier detection method ("zscore" or "iqr").
        threshold: Threshold for outlier detection.

    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer configured with the appropriate outlier detection method. This transformer can be applied to new data to remove outliers based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    data = await mainDatabase.fetch_dataset(project_id)

    try:
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
        if not pd.api.types.is_numeric_dtype(data[column_name]):
            raise ValueError(f"Column '{column_name}' is not numeric.")
        
        if method == 'iqr':
            def outlier_transform_by_iqr(input_data):
                input_data = input_data.copy()
                Q1 = input_data.quantile(0.25)
                Q3 = input_data.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - threshold * IQR
                upper = Q3 + threshold * IQR
                mask = (input_data[column_name] >= lower) & (input_data[column_name]) <= upper
                return input_data[mask].reset_index(drop=True)  

        elif method == 'zscore':
            def outlier_transform_by_zscore(input_data):
                input_data = input_data.copy()
                mean = input_data[column_name].mean()
                std = input_data[column_name].std()
                z_scores = (input_data[column_name] - mean) / std
                mask = np.abs(z_scores) < threshold
                return input_data[mask].reset_index(drop=True)
            
        else: 
            raise ValueError(f"Unknown method: {method}")
        
        return ("handle_outliers",FunctionTransformer(outlier_transform_by_iqr if method == "iqr" else outlier_transform_by_zscore),[column_name])
    
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
    data = await mainDatabase.fetch_dataset(project_id)
    try:
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
        def datetime_transform(input_data):
            input_data = input_data.copy()
            input_data = pd.to_datetime(input_data, errors='coerce')
            if input_data.isna().all():
                raise ValueError(f"Column '{column_name}' doesn't contain any datetime string instances.")
            return input_data

        return ("parse_datetime",FunctionTransformer(datetime_transform),[column_name])

    except Exception as e:
        print(f"Error in parse_datetime: {e}")

# Tool for handling null values
@tool
async def handle_null_values(
    df: Annotated[pd.DataFrame, "The DataFrame to process"],
    strategy: Annotated[str, "The strategy to handle null values. Options: 'drop', 'fill_value', 'fill_mean', 'knn'."],
    value: Annotated[Optional[float], "The value to fill nulls with (if strategy is 'fill_value')."] = None,
    n_neighbors: Annotated[Optional[int], "Number of neighbors for KNN imputation (if strategy is 'knn')."] = 5
) -> pd.DataFrame:
    """
    Handle null values in a DataFrame using the specified strategy.
    """
    if strategy == "drop":
        return df.dropna()
    elif strategy == "fill_value":
        if value is None:
            raise ValueError("A value must be provided for the 'fill_value' strategy.")
        return df.fillna(value)
    elif strategy == "fill_mean":
        return df.fillna(df.mean())
    elif strategy == "knn":
        imputer = KNNImputer(n_neighbors=n_neighbors)
        return pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

# Tool for removing duplicates
@tool
async def remove_duplicates(
    df: Annotated[pd.DataFrame, "The DataFrame to process"],
    strategy: Annotated[str, "The strategy to handle duplicates. Options: 'rows', 'columns'."],
    subset: Annotated[Optional[List[str]], "List of columns to consider for row duplicates (if strategy is 'rows')."] = None,
    keep: Annotated[Optional[str], "Whether to keep the 'first', 'last', or False (if strategy is 'rows' or 'columns')."] = "first"
) -> pd.DataFrame:
    """
    Remove duplicate rows or columns from a DataFrame using the specified strategy.
    """
    if strategy == "rows":
        return df.drop_duplicates(subset=subset, keep=keep)
    elif strategy == "columns":
        return df.loc[:, ~df.columns.duplicated(keep=keep)]
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    

tools=[
    handle_outliers,
    parse_datetime,
    handle_null_values,
    remove_duplicates,
]

async def tool_node(state):
    tools_by_name = {
        handle_outliers.name: handle_outliers,
        parse_datetime.name: parse_datetime
                    }
    
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
    return {'preprocessing_messages':output_messages,'pipeline':preprocessors}

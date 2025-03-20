import pandas as pd
from langchain_core.messages import ToolMessage
from sklearn.impute import KNNImputer
from typing import Annotated, Optional,Union,List
from sklearn.preprocessing import OneHotEncoder, LabelEncoder,FunctionTransformer,OrdinalEncoder,MinMaxScaler,StandardScaler,RobustScaler
from functools import partial
from helperFunctions import *
from API.Requests import projectRequests
from langchain_core.tools import tool,InjectedToolArg
from sklearn.pipeline import Pipeline
from pipeline_cache import get_cached_pipeline, update_cached_pipeline, remove_project_pipelines,save_model,fetch_model,remove_project_models # leave them


@tool
async def encode_categorical_feature(
    column_name: Annotated[str, 'Column to encode.'],
    method: Annotated[str, 'Method: "onehot" or "ordinal" or "label" (which only works for target variable only)'] = 'onehot',
    sparse: Annotated[bool, 'Whether to return a sparse matrix (for one-hot encoding ONLY).'] = True,
    categorical_columns: Annotated[List[str], 'order of categorical columns (if method is "ordinal").'] = 'auto',
    project_id: Annotated[str,InjectedToolArg] = None,
    drop: Annotated[str, 'Whether to drop the first column (for one-hot encoding ONLY).'] = None
) -> tuple:
    """
    Encodes categorical features and returns a transformer to apply the same encoding to new data.
    Note: label encoding is only for target variable. use onehot or ordinal for features, and label for target variable.
    """
    if method == 'onehot':
        encoder = OneHotEncoder(sparse_output=sparse, handle_unknown='ignore',drop=drop)
    elif method == 'label':
        encoder = CustomLabelEncoder(feature_name=column_name)
    elif method == 'ordinal':
        encoder = OrdinalEncoder(categories=categorical_columns,handle_unknown='use_encoded_value',unknown_value=-1)
    else:
        raise ValueError(f"Unknown method: {method}")
    df=await projectRequests.get_dataset(project_id)
    
    try:
        encoder.fit_transform(df[[column_name]])
    except Exception as e:
        print("Failed Final Test")
        raise e
    return ("Encoder",encoder)

@tool
async def normalize_continous_feature(
    column_name: Annotated[str, 'Column to normalize.'],
    method: Annotated[str, 'Method: "minmax" or "standard" or "log" or "robust"'] = 'minmax',
    project_id: Annotated[str,InjectedToolArg] = None,
    clip: Annotated[bool, 'Whether to clip the new values (THIS PARAMETER IS FOR MINMAX ONLY).'] = False,
    with_mean: Annotated[bool, 'Whether to center the data before scaling (THIS PARAMETER IS FOR STANDARD ONLY).'] = True,
    with_std: Annotated[bool, 'Whether to scale the data to unit variance (THIS PARAMETER IS FOR STANDARD ONLY).'] = True
) -> tuple:
    """
    Normalizes continuous features and returns a transformer to apply the same normalization to new data.
    """
    if method == 'minmax':
        transformer = MinMaxScaler(clip=clip)
    elif method == 'standard':
        transformer = StandardScaler(with_mean=with_mean, with_std=with_std)
    elif method == 'log':
        transformer = FunctionTransformer(log_transform,feature_names_out='one-to-one')
    elif method == 'robust':
        transformer = RobustScaler()    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    df=await projectRequests.get_dataset(project_id)
    try:
        transformer.fit_transform(df[[column_name]])
    except Exception as e:
        print("Failed Final Test")
        raise e
    return ("Scaler",transformer)

@tool
async def handle_outliers(
    column_name: Annotated[str, 'column name to be processed'],
    strategy: Annotated[str, "The strategy to handle outliers. Options: 'remove', 'impute_mean', 'impute_median','winsorize'"],
    project_id: Annotated[str,InjectedToolArg] = None,
    method: Annotated[str, 'Method: "zscore" or "iqr"'] = 'iqr',
    threshold: Annotated[float, 'Threshold for outlier detection.'] = 1.5
) -> tuple:
    """
    Detects outliers in the training data and returns a transformer to remove them.
    The transformer is configured with the training data's parameters (e.g., IQR bounds).

    Args:
        column_name: Name of the column to process.
        strategy: The strategy to handle outliers. Options: 'remove', 'impute_mean', 'impute_median', 'log_transform', 'winsorize'.
        project_id: ID of the project to fetch the dataset.
        method: Outlier detection method ("zscore" or "iqr").
        threshold: Threshold for outlier detection.

    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer configured with the appropriate outlier detection method. This transformer can be applied to new data to remove outliers based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """

    try:
        df=await projectRequests.get_dataset(project_id)
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            raise ValueError(f"Column '{column_name}' is not numeric.")
    
        transformer= OutlierTransformer(feature_name=column_name, method=method, strategy=strategy, threshold=threshold)
        
        transformer.fit_transform(df[[column_name]])
        
        if strategy =='remove':
            return (f"Drop Outlier {column_name}",transformer)
        return (f"Outlier Handler",transformer)
    
    except Exception as e:
        print(f"Error in handle_outliers: {e}") #can we make it more descriptive? LLM generated msg?
    
@tool
async def parse_datetime(
    column_name: Annotated[str, 'column name to be processed'],
    additional_features: Annotated[List[str],"List of additional datetime features to extract. Possible values include:'year', 'month', 'day', 'hour', 'minute', 'second', 'weekday', 'week', 'quarter', 'dayofyear', 'is_leap_year', 'is_month_start', 'is_month_end', 'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'."] = [],
    project_id: Annotated[str,InjectedToolArg] = None,
) -> tuple:
    """
    Parses datetime columns and returns a transformer to apply the same parsing to new data.
    
    Args:
        column_name: Name of the column to process.

    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer. This transformer can be applied to new data to parse datetime strings based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    try:
        df=await projectRequests.get_dataset(project_id)
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
        transformer=FunctionTransformer(partial(datetime_transform,additional_features=additional_features),feature_names_out='one-to-one')
        transformer.fit_transform(df[[column_name]])
        return (f"Datetime Parser",transformer)
    
    except Exception as e:
        print(f"Error in parse_datetime: {e}")

@tool
async def handle_null_values(
    column_name: Annotated[str, 'column name to be processed'],
    strategy: Annotated[str, "The strategy to handle null values. only available Options: 'drop', 'value', 'mean', 'median'"],
    project_id: Annotated[str,InjectedToolArg] = None,
    value: Annotated[Optional[Union[float,str,int]], "The value to fill nulls with (if strategy is 'value')."] = None,
    # n_neighbors: Annotated[Optional[int], "Number of neighbors for KNN imputation (if strategy is 'knn')."] = 5,
) -> tuple:
    """
    Handle null values in a DataFrame using the specified strategy.
    
    Args:
        column_name: Name of the column to process.
        strategy : The strategy to handle null values. Options: 'drop', 'value', 'mean'.
        project_id: ID of the project to fetch the dataset.
        value: The value to fill nulls with (if strategy is 'value').
        

    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer configured with the appropriate outlier detection method. This transformer can be applied to new data to remove outliers based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    try:
        df = await projectRequests.get_dataset(project_id)
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
         
        # Check if the strategy and provided value match the column type
        if strategy == "value" and value is not None:
            column_type = df[column_name].dtype
            value_type = type(value)
            print(column_name, column_type, value, value_type)
            
            # For numeric columns
            if pd.api.types.is_numeric_dtype(column_type):
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Column '{column_name}' is numeric but provided value is {value_type}")
            
            # For string/object columns
            elif pd.api.types.is_string_dtype(column_type) or pd.api.types.is_object_dtype(column_type):
                if not isinstance(value, str):
                    raise ValueError(f"Column '{column_name}' is string/object but provided value is {value_type}")
            
            # For datetime columns
            elif pd.api.types.is_datetime64_dtype(column_type):
                if not pd.api.types.is_datetime64_dtype(pd.Series([value])):
                    try:
                        pd.to_datetime(value)  # Try to convert to datetime
                    except:
                        raise ValueError(f"Column '{column_name}' is datetime but provided value cannot be converted to datetime")
                    
        if strategy == "drop":
            return (f"Drop Nulls {column_name}", NullValueTransformer(feature_name=column_name,strategy=strategy,fill_value=value))
        # if strategy == 'knn':
        #     return (f"KNN Imputer {column_name}", KNNImputer(n_neighbors=n_neighbors))
        return (f"Null Handler {column_name}", NullValueTransformer(feature_name=column_name,strategy=strategy,fill_value=value))
    except Exception as e:
        raise e


@tool
async def remove_duplicates(
    column_name: Annotated[str, 'column name to be processed. Either this or Subset should be None']=None,
    project_id: Annotated[str,InjectedToolArg] = None,
    subset: Annotated[Optional[str], "List of columns to consider for row duplicates. Either this or column name should be None"] = None,
    keep: Annotated[Optional[str], "Whether to keep the 'first', 'last', or False (if strategy is 'rows' or 'columns')."] = "first",
) -> tuple:
    """
    Remove duplicate rows or columns from a DataFrame using the specified strategy.

    Args:
        column_name: Name of the column to process.
        project_id: ID of the project to fetch the dataset.
        subset: List of columns to consider for row duplicates. Either this or column name should be None
        keep: Whether to keep the 'first', 'last', or False (if strategy is 'rows' or 'columns').
        
    Returns:
        A tuple of three elements:
        1. Function Name: A string representing the name of the function.
        2. Transformer: An instance of FunctionTransformer configured with the appropriate outlier detection method. This transformer can be applied to new data to remove outliers based on the parameters derived from the training data.
        3. Column Name: A list containing the name of the column that the transformer will process.
    """
    try :
        df = await projectRequests.get_dataset(project_id)
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the dataset.")
        transformer=DropDuplicatesTransformer(subset=subset, column=column_name, keep=keep)
        transformer.fit_transform(df[[column_name] if column_name else subset])
        (f"Drop_Duplicates_{column_name if column_name else subset}",transformer)
    except Exception as e:
        raise ValueError(f"Error in remove_duplicates")

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

    if state['preprocessing_mode']=='X':
        messages = state["X_preprocessing_messages"]
        mode='X'
    else:
        messages = state['Y_preprocessing_messages']
        mode='Y'
    # get the last message of this state
    last_message = messages[-1]
    project_id = state["project_id"]
    preprocessor = await get_cached_pipeline(project_id, mode, state)

    output_messages = []
    for tool_call in last_message.tool_calls:
        print("Tool Name: ",tool_call["name"])
        print("Tool Args: ",tool_call["args"])
        try:
            
            # Invoke the tool based on the tool call
            tool_call["args"]["project_id"] = project_id
            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            
            if tool_result[0][:4]=='Drop':
                print("Droping")
                #Droping should be the first step
                for step in preprocessor.transformers[0][1].steps:
                    if step[0]==tool_result[0]:
                        break
                else:
                    preprocessor.transformers[0][1].steps.append(tool_result)
            
            else:
                print("Preprocessing")
                for transformer in preprocessor.transformers[1:]:
                    if transformer[2][0]==tool_call['args']['column_name']:
                        print("Pipeline Exists")
                        #Pipeline Exists
                        for step in transformer[1].steps:
                            #Pipeline Exists AND Step Exists (Duplicate so skip)
                            if step[0]==tool_result[0]:
                                print("Step Exists")
                                break
                        else:
                            print("Step Does Not Exist")
                            #Pipeline Exists AND Step Does Not Exist
                            transformer[1].steps.append(tool_result)
                            break
                else:
                    print("Pipeline Does Not Exist")
                    #Pipeline Does Not Exist (Create it and add step)
                    pipeline=Pipeline(steps=[tool_result])
                    preprocessor.transformers.append((f"Preprocess_{tool_call['args']['column_name']}",pipeline,[tool_call['args']['column_name']]))
            
            print("Added to Preprocessor")
            output_messages.append(
                ToolMessage(
                    content=f"Preprocessing step completed: {tool_call['name']} for column {tool_call['args']['column_name']} no need to call this function with this exact column again",
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
            print(f"Error in tool_node: {e}")
    await update_cached_pipeline(project_id,mode, preprocessor)
    if mode=='X':
        return {'X_preprocessing_messages':output_messages}
    else:
        return {'Y_preprocessing_messages':output_messages}
"""
preprocessing_tools.py

This module defines various tools for data preprocessing using scikit-learn and pandas.
The tools are designed to handle common preprocessing steps either through predefined functions
or dynamic code generation. Tools are integrated with LangGraph's tool decorator for pipeline integration.

Dependencies:
- pandas
- numpy
- scikit-learn
- langchain_core.tools
- dotenv

Usage:
1. Ensure required dependencies are installed.
2. Import tools into preprocessing pipeline.
3. Use tool registry to check/execute available preprocessing steps.

Functions:
- Each tool handles specific preprocessing operations (imputation, scaling, encoding, etc.)

Variables:
- logger: Logger instance for logging messages.
"""

from typing import Dict, List, Literal, Annotated
import pandas as pd
from langchain_core.tools import tool, InjectedToolArg
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    StandardScaler, 
    OneHotEncoder,
    MinMaxScaler,
    OrdinalEncoder,
    FunctionTransformer
)
from threading import Lock
import sys
import os
from functools import partial
from helperFunctions import validate_column, make_serializable, datetime_transformer
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','Agents')))
# from API.Requests.projectRequests import get_dataset, update_dataset

tool_lock = Lock()

data = {
    "Survived": [0, 1, 1, 1, 0, 0],
    "Pclass": [3, 1, 3, 1, 3, 3],
    "Name": [
        "Braund, Mr. Owen Harris",
        "Cumings, Mrs. John Bradley (Florence Briggs Thayer)",
        "Heikkinen, Miss. Laina",
        "Futrelle, Mrs. Jacques Heath (Lily May Peel)",
        "Allen, Mr. William Henry",
        "Moran, Mr. James"
    ],
    "Sex": ["male", "female", "female", "female", "male", "male"],
    "Age": [22, 38, 26, 35, 35, None],
    "SibSp": [1, 1, 0, 1, 0, 0],
    "Parch": [0, 0, 0, 0, 0, 0],
    "Ticket": ["A/5 21171", "PC 17599", "STON/O2. 3101282", "113803", "373450", "330877"],
    "Fare": [7.25, 71.2833, 7.925, 53.1, 8.05, 8.4583],
    "Cabin": [None, "C85", None, "C123", None, None],
    "Embarked": ["S", "C", "S", "S", "S", "Q"]
}
df = pd.DataFrame(data)


@tool
async def impute_missing(
    column_name: str,
    strategy: Literal["mean", "median", "most_frequent", "constant"] = "mean",
    project_id: Annotated[str, InjectedToolArg] = None
) -> Dict:
    """Handle missing values in numeric columns using specified strategy."""
    try:
        #df = await get_dataset(project_id)
        validate_column(df, column_name, "numeric")
        
        imputer = SimpleImputer(strategy=strategy)
        df[column_name] = imputer.fit_transform(df[[column_name]])
        
        # await update_dataset(project_id, df)
        return {
            "status": "success",
            "message": f"Imputed missing values in {column_name} using {strategy}",
            "transformed_data": make_serializable(df[column_name].head())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
async def standard_scale(
    column_name: str,
    project_id: Annotated[str, InjectedToolArg] = None
) -> Dict:
    """Standardize numeric features by removing mean and scaling to unit variance."""
    try:
        #df = await get_dataset(project_id)
        validate_column(df, column_name, "numeric")
        
        scaler = StandardScaler()
        df[column_name] = scaler.fit_transform(df[[column_name]])
        
        #await update_dataset(project_id, df)
        return {
            "status": "success",
            "message": f"Standard scaled {column_name}",
            "transformed_data": make_serializable(df[column_name].head())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
async def onehot_encode(
    column_name: str,
    handle_unknown: Literal["error", "ignore"] = "ignore",
    project_id: Annotated[str, InjectedToolArg] = None
) -> Dict:
    """One-hot encode categorical features into binary columns."""
    try:
        #df = await get_dataset(project_id)
        validate_column(df, column_name, "categorical")
        
        encoder = OneHotEncoder(handle_unknown=handle_unknown, sparse_output=False)
        encoded = encoder.fit_transform(df[[column_name]])
        
        df = df.drop(columns=[column_name])
        encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out([column_name]))
        df = pd.concat([df, encoded_df], axis=1)
        
        #await update_dataset(project_id, df)
        return {
            "status": "success",
            "message": f"One-hot encoded {column_name}",
            "new_columns": list(encoded_df.columns)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
async def extract_datetime_features(
    column_name: str,
    features: List[Literal[
        "year", "month", "day", "hour", "minute", "second",
        "weekday", "week", "quarter", "dayofyear", "is_leap_year",
        "is_month_start", "is_month_end", "is_quarter_start",
        "is_quarter_end", "is_year_start", "is_year_end"
    ]],
    date_format: str = "%d-%m-%Y",
    project_id: Annotated[str, InjectedToolArg] = None
) -> Dict:
    """Enhanced datetime parsing and feature extraction with transformer support."""
    try:
        #df = await get_dataset(project_id)
        validate_column(df, column_name, "string")
        
        original_series = df[column_name].copy()
        
        df[column_name] = pd.to_datetime(
            df[column_name],
            format=date_format,
            errors='coerce'
        )
        
        null_mask = df[column_name].isna()
        if null_mask.any():
            error_count = null_mask.sum()
            sample_errors = original_series[null_mask].head(3).tolist()
            raise ValueError(
                f"Failed to parse {error_count} values. "
                f"Examples: {sample_errors}. "
                f"Expected format: {date_format} (e.g., 31-12-2023)"
            )
        
        df = datetime_transformer(df, features, column_name)
        
        transformer = FunctionTransformer(
            func=partial(datetime_transformer, features=features, column_name=column_name),
            feature_names_out='one-to-one'
        )
        transformer.fit(df[[column_name]])
        
        #await update_dataset(project_id, df)
        new_columns = [f"{column_name}_{feat}" for feat in features]
        
        return {
            "status": "success",
            "message": f"Extracted {len(features)} datetime features from {column_name}",
            "new_columns": new_columns,
            "sample_data": {col: make_serializable(df[col].head()) for col in new_columns},
            "transformer_config": {
                "name": "DateTimeFeatureExtractor",
                "features": features,
                "source_column": column_name,
                "date_format": date_format
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "expected_format": date_format,
            "example_valid_date": "31-12-2023",
            "error_type": "DATETIME_PARSING_ERROR"
        }

@tool
async def text_cleanup(
    column_name: str,
    steps: List[Literal["lowercase", "remove_urls", "remove_special_chars"]],
    project_id: Annotated[str, InjectedToolArg] = None
) -> Dict:
    """Perform specified text cleaning operations on text column."""
    try:
        #df = await get_dataset(project_id)
        text_series = df[column_name].astype(str)
        
        for step in steps:
            if step == "lowercase":
                text_series = text_series.str.lower()
            elif step == "remove_urls":
                text_series = text_series.str.replace(r"http\S+", "", regex=True)
            elif step == "remove_special_chars":
                text_series = text_series.str.replace(r"[^a-zA-Z0-9\s]", "", regex=True)
        
        df[column_name] = text_series
        #await update_dataset(project_id, df)
        return {
            "status": "success",
            "message": f"Cleaned text using {steps}",
            "sample_text": make_serializable(text_series.head())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
async def minmax_scale(
    column_name: str,
    feature_range: tuple = (0, 1),
    project_id: Annotated[str, InjectedToolArg] = None
) -> Dict:
    """Scale numeric features to specified range (default 0-1)."""
    try:
        #df = await get_dataset(project_id)
        validate_column(df, column_name, "numeric")
        
        if df[column_name].nunique() == 1:
            raise ValueError(f"Cannot scale constant column '{column_name}'")

        scaler = MinMaxScaler(feature_range=feature_range)
        df[column_name] = scaler.fit_transform(df[[column_name]])
        
        #await update_dataset(project_id, df)
        return {
            "status": "success",
            "message": f"MinMax scaled {column_name} to range {feature_range}",
            "transformed_data": make_serializable(df[column_name].head()),
            "scaler_params": {
                "data_min": scaler.data_min_[0],
                "data_max": scaler.data_max_[0],
                "feature_range": scaler.feature_range
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": "SCALING_ERROR"
        }

@tool
async def ordinal_encode(
    column_name: str,
    handle_unknown: Literal["error", "use_encoded_value"] = "error",
    unknown_value: int = -1,
    project_id: Annotated[str, InjectedToolArg] = None
) -> Dict:
    """Encode categorical features as ordinal integers."""
    try:
        #df = await get_dataset(project_id)
        validate_column(df, column_name, "categorical")
        
        encoder = OrdinalEncoder(
            handle_unknown=handle_unknown,
            unknown_value=unknown_value
        )
        
        encoded = encoder.fit_transform(df[[column_name]])
        df[column_name] = encoded.ravel()
        
        #await update_dataset(project_id, df)
        return {
            "status": "success",
            "message": f"Ordinal encoded {column_name}",
            "mapping": dict(zip(
                encoder.categories_[0], 
                range(len(encoder.categories_[0]))
            )),
            "transformed_data": make_serializable(df[column_name].head())
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": "ENCODING_ERROR"
        }

tools = [
    impute_missing,
    standard_scale,
    minmax_scale,
    onehot_encode,
    ordinal_encode,
    extract_datetime_features,
    text_cleanup
]

async def tool_node(state) -> Literal["caller", "__end__"]:
    """Node for invoking preprocessing tools based on state."""
    tools_by_name = {tool.name: tool for tool in tools}
    messages = state["messages"]
    last_message = messages[-1]
    
    try:
        async with tool_lock:
            tool_name = last_message.tool_call["name"]
            args = last_message.tool_call["args"]
            args["project_id"] = state["project_id"]
            
            result = await tools_by_name[tool_name].ainvoke(args)
            
            if result["status"] == "success":
                return {"next": "__end__", "preprocessing_result": result}
            return {"next": "caller", "error": result["message"]}
            
    except Exception as e:
        return {"next": "caller", "error": str(e)}
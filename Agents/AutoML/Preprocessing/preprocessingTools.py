import json
import yfinance as yf
import requests
import pandas as pd
import streamlit as st
from io import StringIO
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode     
from typing import Annotated
import sys
from pathlib import Path
import numpy as np
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import train_test_split

@tool
async def syntethic_function(
    parameter_1:Annotated[str,'description of parameter 1'],
    parameter_2: Annotated[bool,'description of parameter 2']=False
    ):
    """
        Retrieves the latest news for a given stock ticker.
        Args:
            ticker (str): The stock ticker symbol for which to retrieve news.
            more (bool, optional): If True, retrieves more detailed news information. Defaults to False.
        Returns:
            str: A summary of the latest news for the specified stock ticker. If more is True, returns a message indicating the detailed news information.
        """
    # This is a synthetic tools for demonstration purposes. Each function should have a docstring and should describe each parameter as shown above
    

@tool
async def handle_outliers(
    data: Annotated[pd.DataFrame, 'Input dataset (training data).'],
    method: Annotated[str, 'Method: "zscore" or "iqr"'] = 'iqr',
    threshold: Annotated[float, 'Threshold for outlier detection.'] = 1.5
    #train_size: Annotated[float, 'Fraction of data to use for training.'] = 0.8,
) -> FunctionTransformer:
    """
    Detects outliers in the training data and returns a transformer to remove them.
    The transformer is configured with the training data's parameters (e.g., IQR bounds).
    """
    #train_data, val_data = train_test_split(data, train_size=train_size, random_state=42)
    #numeric_data = train_data.select_dtypes(include=[np.number])
    numeric_data = data.select_dtypes(include=[np.number])


    if method == 'iqr':
        Q1 = numeric_data.quantile(0.25)
        Q3 = numeric_data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - threshold * IQR
        upper = Q3 + threshold * IQR

        def outlier_transform(input_data):
            input_data_numeric = input_data.select_dtypes(include=[np.number])
            mask = ~((input_data_numeric < lower) | (input_data_numeric > upper)).any(axis=1)
            return input_data[mask].reset_index(drop=True)

    elif method == 'zscore':
        mean = numeric_data.mean()
        std = numeric_data.std()
        threshold = threshold  

        def outlier_transform(input_data):
            input_data_numeric = input_data.select_dtypes(include=[np.number])
            z_scores = (input_data_numeric - mean) / std
            mask = (np.abs(z_scores) < threshold).all(axis=1)
            return input_data[mask].reset_index(drop=True)

    else:
        raise ValueError(f"Unknown method: {method}")

    return FunctionTransformer(outlier_transform)

@tool
async def parse_datetime(
    data: Annotated[pd.DataFrame, 'Input dataset (training data).'],
    extract_features: Annotated[bool, 'Extract features like year, month, etc.'] = True,
    #datetime_columns: Annotated[list, 'List of datetime columns to parse.'],
    #train_size: Annotated[float, 'Fraction of data to use for training.'] = 0.8,
) -> FunctionTransformer:
    """
    Parses datetime columns and returns a transformer to apply the same parsing to new data.
    """
    #train_data, val_data = train_test_split(data, train_size=train_size, random_state=42)
    datetime_columns = data.select_dtypes(include=[np.datetime64]).columns
    def datetime_transform(input_data): # or train_data
        input_data = input_data.copy()
        for col in datetime_columns:
            input_data[col] = pd.to_datetime(input_data[col])
            if extract_features:
                input_data[f'{col}_year'] = input_data[col].dt.year
                input_data[f'{col}_month'] = input_data[col].dt.month
                input_data[f'{col}_day'] = input_data[col].dt.day
        return input_data

    # Return a FunctionTransformer with the transformation logic
    return FunctionTransformer(datetime_transform)
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
    

from sklearn.impute import KNNImputer
from typing import Annotated, Optional, List

# Tool for handling null values
@tool
def handle_null_values(
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
def remove_duplicates(
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
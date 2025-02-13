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
    

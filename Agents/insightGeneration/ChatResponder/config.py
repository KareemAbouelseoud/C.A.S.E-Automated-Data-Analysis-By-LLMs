import os
import re
import json
from io import StringIO
import pandas as pd
from typing import Dict, List, Tuple, Optional
from langchain import hub
from dotenv import load_dotenv
from langchain_experimental.agents import create_pandas_dataframe_agent
from models import InsightCards, InsightCard, DataDescription
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
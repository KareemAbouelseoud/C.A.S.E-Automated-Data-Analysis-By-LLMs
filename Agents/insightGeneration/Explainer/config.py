import os
import re
import json
import pandas as pd
from typing import Dict, List, Tuple, Optional
from langchain import hub
from dotenv import load_dotenv

from models import InsightCards, InsightCard, DataDescription
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
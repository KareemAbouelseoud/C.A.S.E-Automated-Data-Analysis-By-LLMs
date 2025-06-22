import os 
import sys
import re
import json
from io import StringIO
import numpy as np
import pandas as pd
from typing import Dict
from langchain import hub
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from preprocessingModule.pipeline import preprocess_data
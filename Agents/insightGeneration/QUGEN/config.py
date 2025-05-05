import os
import re
import json
import pandas as pd
from typing import Dict
from langchain import hub
from dotenv import load_dotenv
from .prompts import generate_qugen_prompt
from models import InsightCards, InsightCard
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
import sys
import os
import json
import io
import datetime
import bcrypt
import time
from datetime import datetime
from typing import List, Literal, Optional, Dict,Tuple

import numpy as np
import pandas as pd
from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field

def make_serializable(obj):
    """
    Convert an object to a serializable format.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj


# Add the parent directory to the sys.path (do this ONLY ONCE)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataItems import Chat, Recommender, StHistory, SignUpRequest, LoginRequest
from dataModels.project import Project
from dataModels.user import User
from dataModels.visualization import visualizations,ChatViz
from repositories.base_repository import BaseRepository
from Backend.repositories.visualizations_repository import VisualizationRepository
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from services.project_service import ProjectService
from services.user_service import UserService
from services.visualizations_service import visualizationsService

from Agents.Chatbot import pipeline as chatbot_pipeline, recommender
from Database import mainDatabase

# from repositories.dataset_repository import DatasetRepository
# from services.dataset_service import DatasetService
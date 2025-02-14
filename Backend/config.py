import sys
import os
import json
import io
import datetime
import bcrypt
import time
from typing import List, Optional, Dict

import numpy as np
import pandas as pd
from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field

# Add the parent directory to the sys.path (do this ONLY ONCE)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Agents.Chatbot import pipeline as chatbot_pipeline, recommender
from Agents.codeGeneration import pipeline 
from Database import mainDatabase
from dataItems import Chat, Recommender, StHistory, SignUpRequest, LoginRequest
from dataModels.project import Project, Dataset
from dataModels.user import User
from repositories.chat_repository import ChatRepository
from repositories.project_repository import ProjectRepository
from repositories.dataset_repository import DatasetRepository
from repositories.user_repository import UserRepository
from services.dataset_service import DatasetService
from services.project_service import ProjectService
from services.user_service import UserService
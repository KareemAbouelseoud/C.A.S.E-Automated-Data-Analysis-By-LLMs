"""
This file contains the data items used in the application.
"""
from typing import  Optional,List
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str

class SignUpRequest(BaseModel):
    first_name:str 
    last_name:str
    email:str
    username:str
    password:str
    
class StHistory(BaseModel):
    project_id:str
    last_conv:str

class CreateProject(BaseModel):
    name:str
    user_id: str

class Recommender(BaseModel):
    prompt:str
    project_id:str
    thread_id:str

class Chat(BaseModel):
    prompt:str
    project_id:str
    thread_id:str

class Train(BaseModel):
    target_feature:str
    training_features:List[str]
    mode:str
    user_input:Optional[str]=None
class DatasetVis(BaseModel):
    column_name:str
    plot_type:Optional[str]=None
class SplitDistribution(BaseModel):
    train_size: int
    test_size: int
    val_size: int = 0
    total_rows: int = None

class ClassificationModel(BaseModel):
    accuracy: float
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None

class Predict(BaseModel):
    model_name: str
    data: List[dict]
    feature_columns: Optional[List[str]] = None
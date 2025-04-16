"""
This file contains the data items used in the application.
"""
from typing import  Optional,List
from pydantic import BaseModel


class createDashboard(BaseModel):
    project_id: str
    data_report: str
    features: Optional[List[str]]=None

class Chat(BaseModel):
    project_id:Optional[str]=None
    thread_id:Optional[str]=None
    prompt:str

class Recommender(BaseModel):
    prompt:str
    project_id:str
    thread_id:str
class Feedback(BaseModel):
    feedback:List[str]
    thread_id:str
    user_id:str
    project_id:Optional[str]=None
    description:Optional[str]=None
class SaveInsights(BaseModel):
    insight_cards: List[object]
    advanced_insight_cards : dict
    insights_explanation: dict
    num_cards: int
class Train(BaseModel):
    target_feature:str
    training_features:List[str]
    mode:str
    user_input:Optional[str]=None
    project_id:Optional[str]=None
    data_report:Optional[str]=None

class PredictRequest(BaseModel):
    model_id: str
    data: List[dict]  # List of dict with column name and value
    feature_columns: Optional[List[str]]=None

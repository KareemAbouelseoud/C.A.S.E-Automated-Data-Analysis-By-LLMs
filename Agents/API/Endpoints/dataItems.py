"""
This file contains the data items used in the application.
"""
from typing import  Optional,List
from pydantic import BaseModel


class createDashboard(BaseModel):
    dataframe: str
    data_report: str

class Chat(BaseModel):
    messages:Optional[str]=None
    data_report:Optional[str]=None
    project_id:Optional[str]=None

class Recommender(BaseModel):
    prompt:str
    data_report:str
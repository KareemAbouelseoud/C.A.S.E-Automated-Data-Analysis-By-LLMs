"""
This file contains the data items used in the application.
"""
from typing import  Optional,List
from pydantic import BaseModel


class createDashboard(BaseModel):
    dataframe: str
    data_report: str

class Chat(BaseModel):
    project_id:Optional[str]=None
    thread_id:Optional[str]=None
    prompt:str

class Recommender(BaseModel):
    prompt:str
    data_report:str
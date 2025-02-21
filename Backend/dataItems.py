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

class Chat(BaseModel):
    prompt:str
    messages:Optional[str]=None
    project_id:str

class Train(BaseModel):
    target_feature:str
    training_features:List[str]
    mode:str
    user_input:Optional[str]=None

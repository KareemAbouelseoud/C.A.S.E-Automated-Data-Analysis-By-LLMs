# models/user.py
from typing import List, Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,populate_by_name=True) #Add this line
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    username:str
    first_name:str
    last_name:str
    email:str
    password:str
    Project:List[str]
# models/project.py
from typing import List, Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# class Dataset:
#     def __init__(self, name: str, project_id: str, data_type: str, _id: ObjectId = None):
#         self.id = str(_id) if _id else None
#         self.name = name
#         self.data_type = data_type

#     def to_dict(self):
#         return {
#             "_id": ObjectId(self.id) if self.id else None,
#             "name": self.name,
#             "project_id": self.project_id,
#             "data_type": self.data_type
#         }

#     @classmethod
#     def from_dict(cls, data):
#         return cls(
#             name=data["name"],
#             project_id=data["project_id"],
#             data_type=data["data_type"],
#             _id=data.get("_id")
#         )

class Chat(BaseModel):
    last_date:datetime
    messages:Optional[str]=None

class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,populate_by_name=True) #Add this line
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    name: str
    Dataset: str
    user_id: str  # Reference to the User model
    streamlit_Chat:Optional[Chat]= Field(default=None, alias="streamlit_Chat")
    model_Chat:Optional[Chat]= Field(default=None, alias="model_Chat")
    data_report:Optional[str]= Field(default=None, alias="data_report")
    dataset_description:Optional[str]= Field(default=None, alias="dataset_description")
    created_Date:Optional[datetime]= Field(default=None, alias="created_Date")
    
    @classmethod
    def from_mongo(cls, document):
        """Convert MongoDB document to Project model with string ID."""
        document["id"] = ObjectId(document["_id"])  # Convert ObjectId to string
        return cls(**document)
    
    @classmethod
    def from_dict(cls, document):
        """Convert MongoDB document to Project model with string ID."""
        document["id"] = ObjectId(document["id"])  # Convert ObjectId to string
        document["created_Date"] = datetime.strptime(document["created_Date"],"%d %B %Y")  # Convert ObjectId to string
        return cls(**document)
    

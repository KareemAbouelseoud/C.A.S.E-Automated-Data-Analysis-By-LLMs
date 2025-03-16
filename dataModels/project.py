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
    #TODO: Make the chat saved as List not string
    last_update:datetime = Field(default=datetime.now(), alias="last_update")
    messages:Optional[str]=Field(default=None, alias="messages")

class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,populate_by_name=True) #Add this line
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    name: Optional[str]= Field(default=None, alias="name")
    Dataset: Optional[str] = None
    user_id: str  # Reference to the User model
    streamlit_Chat:Optional[Chat]= Field(default=Chat(last_update=datetime.now()), alias="streamlit_Chat")
    model_Chat:Optional[Chat]= Field(default=Chat(last_update=datetime.now()), alias="model_Chat")
    data_report:Optional[str]= Field(default=None, alias="data_report")
    dataset_description:Optional[str]= Field(default=None, alias="dataset_description")
    created_Date:Optional[datetime]= Field(default=None, alias="created_Date")
    thread_id: Optional[str] = Field(default=None, alias="thread_id")

    #autoML
    Xpreproceesing_pipeline: Optional[List[str]] = Field(default=[], alias="Xpreproceesing_pipeline")
    Ypreproceesing_pipeline: Optional[List[str]] = Field(default=[], alias="Ypreproceesing_pipeline")
    model: Optional[List[str]] = Field(default=None, alias="model")
    model_report: Optional[str] = Field(default=None, alias="model_report")

    
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
        document["model_Chat"]["last_update"] = datetime.strptime(document["model_Chat"]["last_update"],"%d %B %Y")  # Convert ObjectId to string 
        document["streamlit_Chat"]["last_update"] = datetime.strptime(document["streamlit_Chat"]["last_update"],"%d %B %Y")  # Convert ObjectId to string 
        # Only process thread_id if it exists in the document
        if "thread_id" in document and document["thread_id"] is not None:
            document["thread_id"] = str(document["thread_id"])
        return cls(**document)
    

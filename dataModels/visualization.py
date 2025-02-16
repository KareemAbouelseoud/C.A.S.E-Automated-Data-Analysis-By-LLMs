from typing import List, Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field
class ChatViz(BaseModel):
    id:str
    viz:str

class visualizations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,populate_by_name=True) #Add this line
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id:str
    project_id:str
    Auto_generated_viz:Optional[List[str]]= Field(default=[], alias="Auto_generated_viz")
    Chat_visualizations:Optional[List[ChatViz]]= Field(default=[], alias="Chat_visualizations")
    
    @classmethod
    def from_mongo(cls, document):
        """Convert MongoDB document to Project model with string ID."""
        document["id"] = ObjectId(document["_id"])  # Convert ObjectId to string
        return cls(**document)
# models/project.py
from bson.objectid import ObjectId

class Dataset:
    def __init__(self, name: str, project_id: str, data_type: str, _id: ObjectId = None):
        self.id = str(_id) if _id else None
        self.name = name
        self.data_type = data_type

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "name": self.name,
            "project_id": self.project_id,
            "data_type": self.data_type
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            project_id=data["project_id"],
            data_type=data["data_type"],
            _id=data.get("_id")
        )

# models/chat.py

from datetime import datetime

class Chat:
    def __init__(self, user_id: str, message: str, timestamp: datetime = None, _id: ObjectId = None):
        self.id = str(_id) if _id else None
        self.user_id = user_id  # Reference to the User model
        self.message = message
        self.timestamp = timestamp if timestamp else datetime.utcnow()  # Store timestamp in UTC

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["user_id"],
            message=data["message"],
            timestamp=data.get("timestamp"),
            _id=data.get("_id")
        )

class Project:
    def __init__(self, name: Dataset, Dataset: str, user_id: str, _id: ObjectId = None):
        self.id = str(_id) if _id else None
        self.name = name
        self.Dataset = Dataset
        self.user_id = user_id  # Reference to the User model

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "name": self.name,
            "Dataset": self.Dataset,
            "user_id": self.user_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            Dataset=data["Dataset"],
            user_id=data["user_id"],
            _id=data.get("_id")
        )


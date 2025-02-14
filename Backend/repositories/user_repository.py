# repositories/user_repository.py
from typing import Optional, List

from bson.objectid import ObjectId

from .base_repository import BaseRepository
from dataModels.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__("Users")

    async def get_by_id(self, id: str) -> Optional[User]:
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            return User(**document)
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        document = await self.collection.find_one({"username":username })
        print(document)
        if document!=None:
            return User(**document)
        return None

    async def get_all(self) -> List[User]:
        users = []
        async for document in await self.collection.find():
            users.append(User(**document))
        return users

    async def create(self, user: User) -> User:
        result = await self.collection.insert_one(user.model_dump())
        user.id = str(result.inserted_id)  # Set the ID after insertion
        return user
   
    async def Filter(self,filter:dict)->List[User]:
        filtered_Items=[]
        async for document in await self.collection.find(filter):
            filtered_Items.append(User(**document))
        return filtered_Items

    
    async def update(self, id: str, user: User) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": user.to_dict()})
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
from typing import Optional, List

from bson.objectid import ObjectId

from .base_repository import BaseRepository
from dataModels.project import Chat

class ChatRepository(BaseRepository[Chat]):
    def __init__(self, database):
        super().__init__("chats", database)

    async def get_by_id(self, id: str) -> Optional[Chat]:
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            return Chat.from_dict(document)
        return None

    async def get_all(self) -> List[Chat]:
        chats = []
        async for document in self.collection.find():
            chats.append(Chat.from_dict(document))
        return chats

    async def create(self, chat: Chat) -> Chat:
        result = await self.collection.insert_one(chat.to_dict())
        chat.id = str(result.inserted_id)
        return chat

    async def update(self, id: str, chat: Chat) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": chat.to_dict()})
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
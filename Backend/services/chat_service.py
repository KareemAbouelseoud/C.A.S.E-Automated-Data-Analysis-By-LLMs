from typing import List, Optional

from dataModels.project import Chat
from repositories.chat_repository import ChatRepository

class ChatService:
    def __init__(self, chat_repository: ChatRepository):
        self.chat_repository = chat_repository

    async def get_chat(self, id: str) -> Optional[Chat]:
        return await self.chat_repository.get_by_id(id)

    async def get_chats(self) -> List[Chat]:
        return await self.chat_repository.get_all()

    async def create_chat(self, chat: Chat) -> Chat:
        return await self.chat_repository.create(chat)

    async def update_chat(self, id: str, chat: Chat) -> bool:
        return await self.chat_repository.update(id, chat)

    async def delete_chat(self, id: str) -> bool:
        return await self.chat_repository.delete(id)
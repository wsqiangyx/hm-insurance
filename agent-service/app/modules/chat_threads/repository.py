from sqlalchemy.ext.asyncio import AsyncSession
from .models import ChatThreads

class ChatThreadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 新建会话
    async def add(self, chat_thread: ChatThreads):
        self.session.add(chat_thread)
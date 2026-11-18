from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import ChatThreads

class ChatThreadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 新建会话
    async def add(self, chat_thread: ChatThreads):
        self.session.add(chat_thread)

    # 查询会话列表
    async def list_by_user(self, user_id: int) -> list[ChatThreads]:
        # 1、根据userid查询列表
        result = await self.session.scalars(
            select(ChatThreads)
            .where(ChatThreads.user_id == user_id)
            .order_by(
                ChatThreads.updated_at.desc(),
                ChatThreads.created_at.desc(),
            )
        )
        # 2、返回查询结果
        return result.all()

    # 重命名会话
    async def required_owner(self, user_id:int, id: UUID) -> ChatThreads:
        """ 校验指定会话是否属于指定用户 """
        result = await self.session.scalar(
            select(ChatThreads)
            .where(ChatThreads.user_id == user_id, ChatThreads.id == id)
        )
        return result

    # 删除会话
    async  def delete(self, thread: ChatThreads) -> None:
        await self.session.delete(thread)

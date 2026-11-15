from sqlalchemy.ext.asyncio import AsyncSession

from .repository import ChatThreadRepository
from .models import ChatThreads
from .exceptions import ChatThreadNotFound

class ChatThreadsService():
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.repository = ChatThreadRepository(session)

    async def add(self, user_id: int, title: str) -> ChatThreads:
        # 用上下文管理，卡其事务，运行完成，自动commit，出现异常，自动rollback
        async with self.session.begin():
            # 创建对象，对象  映射  到数据库 一条数据
            chat_thread = ChatThreads(user_id=user_id, title=title)
            # 新增对象，插入一条数据
            await self.repository.add(chat_thread)
            return chat_thread

    async def list_by_user(self, user_id: int) -> list[ChatThreads]:
        result = await self.repository.list_by_user(user_id)
        return result

    async def rename(self, user_id: int, id: str, title: str) -> ChatThreads:
        async with self.session.begin():
            # 1、查询会话，校验会话是否属于当前用户
            result = await self.repository.required_owner(user_id=user_id, id=id)
            # 结果不存在，抛出自定义异常
            if not result:
                raise ChatThreadNotFound()

            # 2、修改标题
            result.title = title

            # 3、重新查询数据
            await self.session.flush()
            await self.session.refresh(result)
            return result


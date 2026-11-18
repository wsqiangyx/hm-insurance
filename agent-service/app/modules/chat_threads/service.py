from uuid import UUID

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import ChatThreadRepository
from .models import ChatThreads
from .exceptions import ChatThreadNotFound
from .schemas import ChatMessageResponse, ChatHistoryResponse

class ChatThreadsService():
    def __init__(self, session: AsyncSession, agent: CompiledStateGraph):
        self.session: AsyncSession = session
        self.repository = ChatThreadRepository(session)
        self.agent = agent

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

    # 删除会话
    async def delete(self, thread_id: UUID, user_id: int) -> None:
        async with self.session.begin():
            thread = await self.repository.required_owner(id=thread_id, user_id=user_id)
            if not thread:
                raise ChatThreadNotFound()
            # 在刪除会话之前，需要删除会话的历史消息（State的所有快照）
            await self.agent.checkpointer.adelete_thread(thread_id=thread_id)
            # 删除会话
            await self.session.delete(thread)

    async def get_chat_history(self, user_id: int, thread_id: UUID):
        # 1、校验当前会话是否属于当前会话
        result = await self.repository.required_owner(user_id=user_id, id=thread_id)
        # 结果不存在，抛出自定义异常
        if not result:
            raise ChatThreadNotFound()
        # 2、查询当前会话历史
        state_snapshot = await self.agent.aget_state(config={"configurable":{"thread_id": thread_id}})

        # 3、封装历史消息返回给前端
        messages = []
        for message in state_snapshot.values.get("messages", []):
            # 判断类型，决定role
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                continue
            if message.content:
                messages.append(ChatMessageResponse(role=role, content=message.text))

        return ChatHistoryResponse(thread_id=thread_id, messages=messages)
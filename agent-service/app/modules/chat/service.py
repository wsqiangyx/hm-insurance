from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.chat_threads.exceptions import ChatThreadNotFound
from .schema import ChatRequestSchema
from app.modules.chat_threads.repository import ChatThreadRepository

class ChatService:

    def __init__(self, session:AsyncSession, agent: CompiledStateGraph):
        self.agent = agent
        self.repository = ChatThreadRepository(session)


    async def chat_stream(self, user_id: int, request: ChatRequestSchema):
        """实现Agent流式对话的函数"""

        # 1、校验，判断当前thread_id是否属于当前用户
        chat_thread = await self.repository.required_owner(user_id=user_id, id=request.thread_id)

        if not chat_thread:
            # 指定会话不属于当前用户
            raise ChatThreadNotFound()
        # 1、组织消息
        _input = { "messages": [HumanMessage(request.message)]}
        # 2、组织config，实现会话记忆
        config = {"configurable":{"thread_id": request.thread_id}}

        # 3、调用Agent
        response = await self.agent.ainvoke(input=_input, config=config)

        # 4、返回结果
        return response["messages"][-1].content
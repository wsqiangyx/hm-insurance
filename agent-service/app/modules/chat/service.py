from fastapi.sse import ServerSentEvent
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
        # 2、组织消息
        _input = { "messages": [HumanMessage(request.message)]}
        # 3、组织config，实现会话记忆
        config = {"configurable":{"thread_id": request.thread_id}}

        # 4、调用Agent
        stream = await self.agent.astream_events(input=_input, config=config, version="v3")

        # 5、返回结果
        async for message in stream.messages:
            async for chunk in message.text:
                yield ServerSentEvent(data=chunk, event="message")

        yield ServerSentEvent(data="END", event="done")
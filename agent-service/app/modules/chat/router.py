from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.params import Header
from fastapi.sse import EventSourceResponse, ServerSentEvent
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_session
from .schema import ChatRequestSchema
from .service import ChatService

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["与AI对话接口"],
)

def get_chat_service(http_request: Request, session: AsyncSession = Depends(get_session),):
    # 1、创建ChatService
    agent = http_request.app.state.agent
    return ChatService(session=session, agent=agent)

@router.post("", response_class=EventSourceResponse)
async def chat(
        request: ChatRequestSchema,
        user_id: Annotated[int, Header(alias="X-User-Id")],
        service: ChatService = Depends(get_chat_service),
):
    # 2、调用
    async for sse in service.chat_stream(user_id, request):
        yield sse
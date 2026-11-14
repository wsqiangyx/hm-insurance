from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.params import Header
from sqlalchemy.ext.asyncio import AsyncSession
from .service import ChatThreadsService
from .schemas import *
from app.infra.database import get_session

router = APIRouter(
    prefix="/api/v1/chat-threads",
    tags=["会话管理的接口"],
)

def get_service(session: AsyncSession = Depends(get_session)):
    service = ChatThreadsService(session)
    yield service

@router.post("", response_model=ChatThreadsResponse)
async def create_chat_thread(
        request: ChatThreadsCreate,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadsService = Depends(get_service),
) -> ChatThreadsResponse:
    # 2、执行查询
    return await service.add(user_id = user_id, title=request.title,)
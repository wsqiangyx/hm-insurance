from typing import Annotated

from fastapi import Depends, APIRouter,status,Response
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

@router.get("", response_model=list[ChatThreadsResponse])
async def list_by_user(
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadsService = Depends(get_service),
) -> list[ChatThreadsResponse]:
    return await service.list_by_user(user_id = user_id)

@router.patch("/{thread_id}", response_model=ChatThreadsResponse)
async def rename(
        thread_id: str,
        request: ChatThreadsCreate,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadsService = Depends(get_service),
) -> ChatThreadsResponse:
    """重命名会话"""
    return await service.rename(user_id = user_id,id=thread_id, title=request.title)

@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        thread_id: UUID,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadsService = Depends(get_service),
) -> Response:
    """ 删除指定会话 """

    await service.delete(user_id = user_id,thread_id=thread_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
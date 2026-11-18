from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from app.common.schemas import BaseSchema

# 创建会话
class ChatThreadsCreate(BaseSchema):
    title: str = Field(default="新会话", min_length=1, max_length=200)

    # 补充功能，去除空格校验
    @field_validator('title', mode='before')
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return value.strip()

# 响应格式
class ChatThreadsResponse(BaseSchema):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

class ChatMessageResponse(BaseSchema):
    """ 历史消息 """

    role: Literal["user", "assistant"]
    content: str

class ChatHistoryResponse(BaseSchema):
    """ 会话历史响应 """

    thread_id: UUID
    messages: list[ChatMessageResponse]
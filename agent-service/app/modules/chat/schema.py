from uuid import UUID

from pydantic import Field

from app.common.schemas import BaseSchema

# 请求约束
class ChatRequestSchema(BaseSchema):
    """ 基础对话请求 """

    thread_id: UUID
    message: str = Field(min_length=1)
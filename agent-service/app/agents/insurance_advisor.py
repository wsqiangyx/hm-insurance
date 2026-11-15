from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.logging import get_logger

logger = get_logger(__name__)

# 加载环境变量
from app.core.config import settings

SYSTEM_PROMPT = """
你是“安心保”的智能保险顾问。
你需要使用专业、准确、容易理解的语言回答用户的保险问题。
当信息不足时，应先向用户追问，不要编造保险产品或保障内容。
"""

# agent在整个系统中，只初始化一次
async def init_insurance_agent(checkpointer: AsyncPostgresSaver):
    # 初始化模型
    model = init_chat_model(
        model=settings.llm.chat_model,
        model_provider='openai',
        api_key=settings.llm.api_key,
        base_url=settings.llm.base_url,
        extra_body={
            # 关闭思考模式
            "thinking": {
                "type": "disabled"
            }
        }
    )

    # 初始化工具

    # 创建agent，绑定model、tools、checkpointer
    agent = create_agent(
        model=model,
        tools=[],
        checkpointer=checkpointer,
        system_prompt=SYSTEM_PROMPT,
    )
    logger.info("保险顾问Agent初始化完毕~")
    return agent
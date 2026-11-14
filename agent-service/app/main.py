import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import configure_logging,get_logger

# 日志配置
configure_logging(settings.logging.level)

#获取日志记录器
logger = get_logger(__name__)

# 初始化FastAPI
app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
)

# 接口测试，健康测试
@app.get("/health", summary="健康检测接口")
async def health() -> dict[str, str]:
    logger.info("健康检测接口正常调用")
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False
    )
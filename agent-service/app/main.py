from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import configure_logging,get_logger

# 日志配置
configure_logging(settings.logging.level)

#获取日志记录器
logger = get_logger(__name__)

# 初始化生命周期钩子
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("项目启动中，正在初始化。。。")
    from app.infra.database import check_database, close_database
    try:
        # 1、导入数据库管理函数，完成初始化
        await check_database()
        yield
    finally:
        # 关闭
        await close_database()


# 初始化FastAPI
app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan
)

# 挂载路由
from app.modules.product.router import router as product_router
app.include_router(product_router)

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
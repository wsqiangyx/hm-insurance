from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_session
from app.modules.product.models import Product
from .schemas import ProductResponse
from .service import ProductService

router = APIRouter(
    prefix="/api/v1/products",
    tags=["产品管理的相关接口"],
)
@router.get("", response_model=list[ProductResponse])
async def list_products(
        category: str|None = None,
        session: AsyncSession = Depends(get_session),
) -> list[ProductResponse]:
    # 1、创建service
    service = ProductService(session)
    # 2、执行查询
    return await service.list_products(category)
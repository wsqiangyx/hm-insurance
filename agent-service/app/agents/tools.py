from decimal import Decimal

from langchain_core.tools import tool

from app.infra.database import AsyncSessionFactory
from app.modules.product.service import ProductService
from app.modules.product.models import Product
from app.modules.product.schemas import ProductResponse

@tool
async def query_candidate_products(
        categories: list[str],
        premium_min: Decimal | None = None,
        limit_per_category: int = 5
):
    """
    根据险种和保费条件查询可用于推荐的候选保险产品。当用户咨询保险产品或需要保险产品推荐时使用

    Args:
        categories: 保产品分类列表，可选值为 medical、critical_illness、life、accident
        premium_min: 期最低保费上限，可选参数。只返回最低保费小于该值的产品
        limit_per_category: 每个险种最多返回的产品数量，默认为5

    Returns:
        返回筛选后的保险产品信息列表
    """
    async with AsyncSessionFactory() as session:
        # 1、初始化Service
        service = ProductService(session)
        # 2、调用Service，得到候选列表
        products: list[Product] = await service.list_candidates(categories, premium_min, limit_per_category)
        # 3、返回给AI，将Product数据处理成JSON返回
        return [ProductResponse.model_validate(product).model_dump_json() for product in products]
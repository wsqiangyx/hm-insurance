from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Product

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def query_by_category(self, category: str | None = None) -> list[Product]:
        # 1、动态条件
        # 1.1 产品必须是上架产品
        conditions = [Product.status == "active"]
        # 1.2、如果category不为空，添加分类查询的条件
        if category:
            conditions.append(Product.category == category)

        # 实现查询sql语句
        result = await self.session.execute(
            select(Product).where(*conditions)
            .order_by(Product.id.asc())
        )

        return result.scalars().all()

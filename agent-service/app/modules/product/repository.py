from decimal import Decimal

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

    async def find_candidates(
            self,
            category: str,
            premium_min: Decimal | None,
            limit: int
    ) -> list[Product]:
        conditions = [
            Product.status == "active",
            Product.category == category
        ]
        if premium_min is not None:
            conditions.append(Product.min_premium < premium_min)

        products = await self.session.scalars(
            select(Product).where(*conditions)
            .order_by(Product.min_premium.asc().nullslast(), Product.id.asc())
            .limit(limit)
        )
        return products.all()
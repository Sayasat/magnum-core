from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalog.models import Category, Product


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, name: str, slug: str) -> Category:
        category = Category(
            name=name,
            slug=slug,
        )

        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)

        return category

    async def get_by_id(self, category_id: UUID) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_categories(self) -> list[Category]:
        stmt = select(Category).order_by(Category.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, category: Category) -> Category:
        await self.session.flush()
        await self.session.refresh(category)
        return category


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        category_id: UUID,
        name: str,
        slug: str,
        description: str | None,
        price,
        sku: str,
        stock_quantity: int,
    ) -> Product:
        product = Product(
            category_id=category_id,
            name=name,
            slug=slug,
            description=description,
            price=price,
            sku=sku,
            stock_quantity=stock_quantity,
        )

        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)

        return product

    async def get_by_id(self, product_id: UUID) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Product | None:
        stmt = select(Product).where(Product.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_products(
        self,
        *,
        search: str | None = None,
        category_id: UUID | None = None,
    ) -> list[Product]:
        stmt = select(Product)

        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                )
            )

        stmt = stmt.order_by(Product.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, product: Product) -> Product:
        await self.session.flush()
        await self.session.refresh(product)
        return product
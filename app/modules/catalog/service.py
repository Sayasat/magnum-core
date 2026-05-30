from typing import Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
import json
from app.core.redis import redis_client

from app.shared.exceptions import NotFoundException, ConflictException
from app.modules.catalog.models import Category, Product
from app.modules.catalog.repository import CategoryRepository, ProductRepository

from app.modules.catalog.schemas import CategoryCreate, CategoryUpdate, ProductUpdate, ProductCreate, ProductResponse


class CategoryService:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    async def create_category(self, data: CategoryCreate) -> Category:
        existing = await self.category_repository.get_by_slug(data.slug)

        if existing:
            raise ConflictException("Category with this slug already exists")

        return await self.category_repository.create(
            name=data.name,
            slug=data.slug,
        )

    async def list_categories(self) -> list[Category]:
        return await self.category_repository.list_categories()

    async def get_category_by_id(self, category_id: UUID) -> Category:
        category = await self.category_repository.get_by_id(category_id)

        if not category:
            raise NotFoundException("Category not found")
        return category

    async def update_category(self, category_id: UUID, data: CategoryUpdate,) -> Category:
        category = await self.get_category_by_id(category_id)

        update_data = data.model_dump(exclude_unset=True)

        if "slug" in update_data:
            existing = await self.category_repository.get_by_slug(update_data["slug"])
            if existing and existing.id != category.id:
                raise ConflictException("Category with this slug already exists")

        for field, value in update_data.items():
            setattr(category, field, value)

        return await self.category_repository.update(category)

CACHE_TTL = 60
class ProductService:
    def __init__(self, product_repository: ProductRepository, category_repository: CategoryRepository):
        self.product_repository = product_repository
        self.category_repository = category_repository

    @staticmethod
    async def clear_products_cache_by_category(category_id: UUID | None = None):
        """
        Очистка кеша для всех продуктов.
        Если передан category_id, удаляем только ключи с этой категорией.
        """
        if category_id:
            pattern = f"products:{category_id}:*"
        else:
            pattern = "products:*"

        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)

    async def create_product(self, data: ProductCreate) -> Product:
        category = await self.category_repository.get_by_id(data.category_id)
        if not category:
            raise NotFoundException("Category not found")
        existing_slug = await self.product_repository.get_by_slug(data.slug)
        if existing_slug:
            raise ConflictException("Product with this slug already exists")
        existing_sku = await self.product_repository.get_by_sku(data.sku)
        if existing_sku:
            raise ConflictException("Product with this SKU already exists")
        await self.clear_products_cache_by_category(data.category_id)

        return await self.product_repository.create(
            category_id=data.category_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            price=data.price,
            sku=data.sku,
            stock_quantity=data.stock_quantity,
        )

    async def list_products(self, *, search: str | None = None, category_id: UUID | None = None,
                            limit: int = 20, offset: int = 0,) -> tuple[list[ProductResponse], Any] | tuple[
        list[Product], int]:
        cache_key = f"products:{search}:{category_id}:{limit}:{offset}"
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            products = [ProductResponse.model_validate(item) for item in data["items"]]
            total = data["total"]
            return products, total
        # Получаем данные из базы
        products = await self.product_repository.list_products(
            search=search, category_id=category_id, limit=limit,offset=offset,
        )
        total = await self.product_repository.count_products(
            search=search, category_id=category_id,
        )
        # Сериализация UUID и Decimal перед json.dumps
        cache_value = {
            "items": [
                {
                    k: str(v) if isinstance(v, (UUID, Decimal, datetime)) else v
                    for k, v in ProductResponse.model_validate(p).model_dump().items()
                }
                for p in products
            ],
            "total": total,
        }
        await redis_client.set(cache_key, json.dumps(cache_value), ex=CACHE_TTL)
        return products, total

    async def get_product_by_id(self, product_id: UUID) -> Product:
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product not found")
        return product

    async def update_product(self, product_id: UUID, data: ProductUpdate,) -> Product | None:
        product = await self.get_product_by_id(product_id)
        update_data = data.model_dump(exclude_unset=True)

        if "category_id" in update_data:
            category = await self.category_repository.get_by_id(update_data["category_id"])
            if not category:
                raise NotFoundException("Category not found")

        if "slug" in update_data:
            existing_slug = await self.product_repository.get_by_slug(update_data["slug"])
            if existing_slug and existing_slug.id != product.id:
                raise ConflictException("Product with this SLUG already exists")

        if "sku" in update_data:
            existing_sku = await self.product_repository.get_by_sku(update_data["sku"])
            if existing_sku and existing_sku.id != product.id:
                raise ConflictException("Product with this SKU already exists")

        for field, value in update_data.items():
            setattr(product, field, value)

        await self.clear_products_cache_by_category(data.category_id)
        return await self.product_repository.update(product)








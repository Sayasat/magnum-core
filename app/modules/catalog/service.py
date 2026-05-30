from typing import Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
import json

from app.core.config import settings
from app.core.redis import redis_client
from app.shared.exceptions import NotFoundException, ConflictException
from app.modules.catalog.models import Category, Product
from app.modules.catalog.repository import CategoryRepository, ProductRepository

from app.modules.catalog.schemas import CategoryCreate, CategoryUpdate, ProductUpdate, ProductCreate, ProductResponse, \
    CategoryResponse


class CategoryService:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    @staticmethod
    async def clear_categories_cache() -> None:
        keys = await redis_client.keys("catalog:categories:*")
        if keys:
            await redis_client.delete(*keys)

    @staticmethod
    def _serialize_response(response) -> dict[str, Any]:
        return {
            key: str(value) if isinstance(value, (UUID, Decimal, datetime)) else value
            for key, value in response.model_dump().items()
        }

    async def create_category(self, data: CategoryCreate) -> Category:
        existing = await self.category_repository.get_by_slug(data.slug)
        if existing:
            raise ConflictException("Category with this slug already exists")
        category_create = await self.category_repository.create(name=data.name,slug=data.slug,)
        await self.clear_categories_cache()
        return category_create

    async def list_categories(self) -> list[CategoryResponse]:
        cache_key = "catalog:categories:list"
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [CategoryResponse.model_validate(item) for item in data]

        categories = await self.category_repository.list_categories()

        cache_value = [
            self._serialize_response(CategoryResponse.model_validate(category)) for category in categories
        ]

        await redis_client.set(cache_key, json.dumps(cache_value), ex=settings.CACHE_TTL_CATEGORIES,)
        return [CategoryResponse.model_validate(category) for category in categories]

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

        category = await self.category_repository.update(category)
        await self.clear_categories_cache()
        return category


class ProductService:
    def __init__(self, product_repository: ProductRepository, category_repository: CategoryRepository):
        self.product_repository = product_repository
        self.category_repository = category_repository

    @staticmethod
    async def clear_products_cache() -> None:
        keys = await redis_client.keys("catalog:products:*")
        if keys:
            await redis_client.delete(*keys)

    @staticmethod
    def _build_products_list_cache_key(*, search: str | None, category_id: UUID | None,
                                       limit: int, offset: int,) -> str:
        return f"catalog:products:list:search={search}:category={category_id}:limit={limit}:offset={offset}"

    @staticmethod
    def _serialize_response(response) -> dict[str, Any]:
        return {
            key: str(value) if isinstance(value, (UUID, Decimal, datetime)) else value
            for key, value in response.model_dump().items()
        }

    @staticmethod
    def _build_product_detail_cache_key(product_id: UUID) -> str:
        return f"catalog:products:detail:{product_id}"

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
        await self.clear_products_cache()

        product = await self.product_repository.create(
            category_id=data.category_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            price=data.price,
            sku=data.sku,
            stock_quantity=data.stock_quantity,
        )
        await self.clear_products_cache()
        return product


    async def list_products(self, *, search: str | None = None, category_id: UUID | None = None,
                            limit: int = 20, offset: int = 0,) -> tuple[list[ProductResponse], Any] | tuple[
        list[Product], int]:
        cache_key = self._build_products_list_cache_key(
            search=search, category_id=category_id, limit=limit, offset=offset,
        )
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            products = [ProductResponse.model_validate(item) for item in data["items"]]
            return products, data["total"]
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
                self._serialize_response(ProductResponse.model_validate(product))
                for product in products
            ],
            "total": total,
        }
        await redis_client.set(cache_key, json.dumps(cache_value), ex=60)
        return [ProductResponse.model_validate(product) for product in products], total


    async def get_product_by_id(self, product_id: UUID) -> ProductResponse:
        cache_key = self._build_product_detail_cache_key(product_id)
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return ProductResponse.model_validate(data)

        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product not found")
        response = ProductResponse.model_validate(product)
        await redis_client.set(
            cache_key,
            json.dumps(self._serialize_response(response)),
            ex=settings.CACHE_TTL_PRODUCTS,
        )
        return response


    async def _get_product_model_by_id(self, product_id: UUID) -> Product:
        product = await self.product_repository.get_by_id(product_id)

        if not product:
            raise NotFoundException("Product not found")

        return product


    async def update_product(self, product_id: UUID, data: ProductUpdate,) -> Product | None:
        product = await self._get_product_model_by_id(product_id)
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

        await self.clear_products_cache()
        return await self.product_repository.update(product)






from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.catalog.repository import CategoryRepository, ProductRepository
from app.modules.catalog.service import CategoryService, ProductService


def get_category_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CategoryRepository:
    return CategoryRepository(session)


def get_product_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProductRepository:
    return ProductRepository(session)


def get_category_service(
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(category_repository)


def get_product_service(
    product_repository: ProductRepository = Depends(get_product_repository),
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> ProductService:
    return ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )
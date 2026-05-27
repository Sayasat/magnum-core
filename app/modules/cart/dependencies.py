from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.cart.repository import CartRepository
from app.modules.cart.service import CartService
from app.modules.catalog.repository import ProductRepository


def get_cart_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CartRepository:
    return CartRepository(session)


def get_product_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProductRepository:
    return ProductRepository(session)


def get_cart_service(
    cart_repository: CartRepository = Depends(get_cart_repository),
    product_repository: ProductRepository = Depends(get_product_repository),
) -> CartService:
    return CartService(
        cart_repository=cart_repository,
        product_repository=product_repository,
    )
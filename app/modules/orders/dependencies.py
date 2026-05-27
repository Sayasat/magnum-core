from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.cart.repository import CartRepository
from app.modules.catalog.repository import ProductRepository
from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService


def get_order_repository(
    session: AsyncSession = Depends(get_db_session),
) -> OrderRepository:
    return OrderRepository(session)


def get_cart_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CartRepository:
    return CartRepository(session)


def get_product_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProductRepository:
    return ProductRepository(session)


def get_order_service(
    order_repository: OrderRepository = Depends(get_order_repository),
    cart_repository: CartRepository = Depends(get_cart_repository),
    product_repository: ProductRepository = Depends(get_product_repository),
) -> OrderService:
    return OrderService(
        order_repository=order_repository,
        cart_repository=cart_repository,
        product_repository=product_repository,
    )
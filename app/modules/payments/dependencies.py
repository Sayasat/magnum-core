from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.orders.repository import OrderRepository
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.service import PaymentService


def get_payment_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PaymentRepository:
    return PaymentRepository(session)


def get_order_repository(
    session: AsyncSession = Depends(get_db_session),
) -> OrderRepository:
    return OrderRepository(session)


def get_payment_service(
    payment_repository: PaymentRepository = Depends(get_payment_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> PaymentService:
    return PaymentService(
        payment_repository=payment_repository,
        order_repository=order_repository,
    )
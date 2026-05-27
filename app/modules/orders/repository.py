from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.orders.enums import OrderStatus
from app.modules.orders.models import Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(
        self,
        *,
        user_id: UUID,
        total_amount: Decimal,
    ) -> Order:
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING_PAYMENT,
        )

        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)

        return order

    async def add_order_item(
        self,
        *,
        order_id: UUID,
        product_id: UUID,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
        total_price: Decimal,
    ) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
        )

        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)

        return item

    async def get_by_id(self, order_id: UUID) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user_id(self, *, user_id: UUID, limit: int = 20, offset: int = 0,) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .limit(limit).offset(offset)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self, *, limit: int = 20, offset: int = 0,) -> list[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .limit(limit).offset(offset)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, order: Order) -> Order:
        await self.session.flush()
        await self.session.refresh(order)

        return order

    async def count_by_user_id(self, user_id: UUID) -> int:
        stmt = select(func.count(Order.id)).where(Order.user_id == user_id)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_all(self) -> int:
        stmt = select(func.count(Order.id))

        result = await self.session.execute(stmt)
        return result.scalar_one()
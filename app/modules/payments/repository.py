from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.enums import PaymentProvider, PaymentStatus
from app.modules.payments.models import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        order_id: UUID,
        amount: Decimal,
        provider: PaymentProvider = PaymentProvider.MOCK,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            amount=amount,
            provider=provider,
            status=PaymentStatus.PENDING,
        )

        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)

        return payment

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_by_order_id(self, order_id: UUID) -> Payment | None:
        stmt = select(Payment).where(
            Payment.order_id == order_id,
            Payment.status == PaymentStatus.PENDING,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, payment: Payment) -> Payment:
        await self.session.flush()
        await self.session.refresh(payment)
        return payment
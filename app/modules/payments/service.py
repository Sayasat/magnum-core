from uuid import UUID

from app.modules.orders.enums import OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.payments.enums import PaymentStatus
from app.modules.payments.models import Payment
from app.modules.payments.repository import PaymentRepository
from app.shared.exceptions import BadRequestException, ForbiddenException, NotFoundException


class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        order_repository: OrderRepository,
    ):
        self.payment_repository = payment_repository
        self.order_repository = order_repository

    async def create_payment_for_order(
        self,
        *,
        user_id: UUID,
        order_id: UUID,
        is_admin: bool = False,
    ) -> Payment:
        order = await self.order_repository.get_by_id(order_id)

        if not order:
            raise NotFoundException("Order not found")

        if not is_admin and order.user_id != user_id:
            raise ForbiddenException("You do not have access to this order")

        if order.status != OrderStatus.PENDING_PAYMENT:
            raise BadRequestException("Payment can be created only for pending payment orders")

        existing_payment = await self.payment_repository.get_pending_by_order_id(order.id)

        if existing_payment:
            return existing_payment

        return await self.payment_repository.create(
            order_id=order.id,
            amount=order.total_amount,
        )

    async def get_payment(
        self,
        *,
        user_id: UUID,
        payment_id: UUID,
        is_admin: bool = False,
    ) -> Payment:
        payment = await self.payment_repository.get_by_id(payment_id)

        if not payment:
            raise NotFoundException("Payment not found")

        order = await self.order_repository.get_by_id(payment.order_id)

        if not order:
            raise NotFoundException("Order not found")

        if not is_admin and order.user_id != user_id:
            raise ForbiddenException("You do not have access to this payment")

        return payment

    async def mark_payment_success(
        self,
        *,
        user_id: UUID,
        payment_id: UUID,
        is_admin: bool = False,
    ) -> Payment:
        payment = await self.get_payment(
            user_id=user_id,
            payment_id=payment_id,
            is_admin=is_admin,
        )

        if payment.status != PaymentStatus.PENDING:
            raise BadRequestException("Only pending payment can be marked as success")

        order = await self.order_repository.get_by_id(payment.order_id)

        if not order:
            raise NotFoundException("Order not found")

        if order.status != OrderStatus.PENDING_PAYMENT:
            raise BadRequestException("Order is not pending payment")

        payment.status = PaymentStatus.SUCCESS
        order.status = OrderStatus.PAID

        await self.order_repository.update(order)
        return await self.payment_repository.update(payment)

    async def mark_payment_failed(
        self,
        *,
        user_id: UUID,
        payment_id: UUID,
        is_admin: bool = False,
    ) -> Payment:
        payment = await self.get_payment(
            user_id=user_id,
            payment_id=payment_id,
            is_admin=is_admin,
        )

        if payment.status != PaymentStatus.PENDING:
            raise BadRequestException("Only pending payment can be marked as failed")

        payment.status = PaymentStatus.FAILED

        return await self.payment_repository.update(payment)
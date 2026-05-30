from decimal import Decimal
from uuid import UUID

from app.core.config import settings
from app.core.redis import redis_client
from app.modules.cart.repository import CartRepository
from app.modules.catalog.repository import ProductRepository
from app.modules.orders.enums import OrderStatus
from app.modules.orders.models import Order
from app.modules.orders.repository import OrderRepository
from app.shared.exceptions import BadRequestException, ForbiddenException, NotFoundException, ConflictException


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        cart_repository: CartRepository,
        product_repository: ProductRepository,
    ):
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    @staticmethod
    def _build_checkout_lock_key(user_id: UUID) -> str:
        return f"orders:checkout:lock:{user_id}"

    async def checkout(self,user_id: UUID) -> Order:
        lock_key = self._build_checkout_lock_key(user_id)
        lock_acquired = await redis_client.set(
            lock_key, "1", ex=settings.CHECKOUT_LOCK_TTL_SECONDS, nx=True,
        )
        if not lock_acquired:
            raise ConflictException("Checkout is already in progress")

        try:
            return await self._checkout(user_id)
        finally:
            await redis_client.delete(lock_key)


    async def _checkout(self, user_id: UUID) -> Order:
        cart = await self.cart_repository.get_by_user_id(user_id)

        if not cart or not cart.items:
            raise BadRequestException("Cart is empty")

        total_amount = Decimal("0.00")

        products_by_id = {}

        for cart_item in cart.items:
            product = await self.product_repository.get_by_id(cart_item.product_id)

            if not product:
                raise NotFoundException("Product not found")

            if not product.is_active:
                raise BadRequestException(f"Product '{product.name}' is not active")

            if product.stock_quantity < cart_item.quantity:
                raise BadRequestException(f"Not enough stock for product '{product.name}'")

            products_by_id[product.id] = product
            total_amount += cart_item.unit_price * cart_item.quantity

        order = await self.order_repository.create_order(
            user_id=user_id,
            total_amount=total_amount,
        )

        for cart_item in cart.items:
            product = products_by_id[cart_item.product_id]

            item_total = cart_item.unit_price * cart_item.quantity

            await self.order_repository.add_order_item(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=item_total,
            )

            product.stock_quantity -= cart_item.quantity
            await self.product_repository.update(product)

        await self.cart_repository.clear_cart(cart.id)

        created_order = await self.order_repository.get_by_id(order.id)

        if not created_order:
            raise NotFoundException("Order not found")

        return created_order

    async def list_user_orders(self, *, user_id: UUID, limit: int=20, offset: int=0,) -> tuple[list[Order],int]:
        orders = await self.order_repository.list_by_user_id(
            user_id=user_id, limit=limit,  offset=offset,)
        total = await self.order_repository.count_by_user_id(user_id)
        return orders, total

    async def list_all_orders(self,*, limit: int = 20, offset: int = 0,) -> tuple[list[Order], int]:
        orders = await self.order_repository.list_all(limit=limit, offset=offset,)
        total = await self.order_repository.count_all()
        return orders, total

    async def get_user_order(
        self,
        *,
        user_id: UUID,
        order_id: UUID,
        is_admin: bool = False,
    ) -> Order:
        order = await self.order_repository.get_by_id(order_id)

        if not order:
            raise NotFoundException("Order not found")

        if not is_admin and order.user_id != user_id:
            raise ForbiddenException("You do not have access to this order")

        return order

    async def cancel_order(
        self,
        *,
        user_id: UUID,
        order_id: UUID,
        is_admin: bool = False,
    ) -> Order:
        order = await self.get_user_order(
            user_id=user_id,
            order_id=order_id,
            is_admin=is_admin,
        )

        if order.status != OrderStatus.PENDING_PAYMENT:
            raise BadRequestException("Only pending payment orders can be cancelled")

        for item in order.items:
            product = await self.product_repository.get_by_id(item.product_id)

            if product:
                product.stock_quantity += item.quantity
                await self.product_repository.update(product)

        order.status = OrderStatus.CANCELLED

        return await self.order_repository.update(order)

    async def complete_order(self, order_id: UUID) -> Order:
        order = await self.order_repository.get_by_id(order_id)

        if not order:
            raise NotFoundException("Order not found")

        if order.status != OrderStatus.PAID:
            raise BadRequestException("Only paid orders can be completed")

        order.status = OrderStatus.COMPLETED

        return await self.order_repository.update(order)
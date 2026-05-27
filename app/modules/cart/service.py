from decimal import Decimal
from uuid import UUID

from app.modules.cart.models import Cart
from app.modules.cart.repository import CartRepository
from app.modules.cart.schemas import (
    AddCartItemRequest,
    CartItemResponse,
    CartResponse,
    UpdateCartItemRequest,
)
from app.modules.catalog.repository import ProductRepository
from app.shared.exceptions import BadRequestException, NotFoundException


class CartService:
    def __init__(
        self,
        cart_repository: CartRepository,
        product_repository: ProductRepository,
    ):
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    async def get_cart(self, user_id: UUID) -> CartResponse:
        cart = await self.cart_repository.get_or_create_by_user_id(user_id)
        if not cart:
            raise NotFoundException("Cart not found")
        return self._build_cart_response(cart)

    async def add_item(
        self,
        *,
        user_id: UUID,
        data: AddCartItemRequest,
    ) -> CartResponse:
        product = await self.product_repository.get_by_id(data.product_id)

        if not product:
            raise NotFoundException("Product not found")

        if not product.is_active:
            raise BadRequestException("Product is not active")

        if product.stock_quantity < data.quantity:
            raise BadRequestException("Not enough product stock")

        cart = await self.cart_repository.get_or_create_by_user_id(user_id)

        existing_item = await self.cart_repository.get_item_by_cart_and_product(
            cart_id=cart.id,
            product_id=product.id,
        )

        if existing_item:
            new_quantity = existing_item.quantity + data.quantity

            if product.stock_quantity < new_quantity:
                raise BadRequestException("Not enough product stock")

            existing_item.quantity = new_quantity
            existing_item.unit_price = product.price

            await self.cart_repository.update_item(existing_item)
        else:
            await self.cart_repository.add_item(
                cart_id=cart.id,
                product_id=product.id,
                quantity=data.quantity,
                unit_price=product.price,
            )

        cart = await self.cart_repository.get_by_user_id(user_id)

        if not cart:
            raise NotFoundException("Cart not found")

        return self._build_cart_response(cart)

    async def update_item(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        data: UpdateCartItemRequest,
    ) -> CartResponse:
        cart = await self.cart_repository.get_or_create_by_user_id(user_id)
        item = await self.cart_repository.get_item_by_id(item_id)

        if not item or item.cart_id != cart.id:
            raise NotFoundException("Cart item not found")

        product = await self.product_repository.get_by_id(item.product_id)

        if not product:
            raise NotFoundException("Product not found")

        if product.stock_quantity < data.quantity:
            raise BadRequestException("Not enough product stock")

        item.quantity = data.quantity
        item.unit_price = product.price

        await self.cart_repository.update_item(item)

        cart = await self.cart_repository.get_by_user_id(user_id)

        if not cart:
            raise NotFoundException("Cart not found")

        return self._build_cart_response(cart)

    async def remove_item(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
    ) -> CartResponse:
        cart = await self.cart_repository.get_or_create_by_user_id(user_id)
        item = await self.cart_repository.get_item_by_id(item_id)

        if not item or item.cart_id != cart.id:
            raise NotFoundException("Cart item not found")

        await self.cart_repository.delete_item(item)

        cart = await self.cart_repository.get_by_user_id(user_id)

        if not cart:
            raise NotFoundException("Cart not found")

        return self._build_cart_response(cart)

    async def clear_cart(self, user_id: UUID) -> CartResponse:
        cart = await self.cart_repository.get_or_create_by_user_id(user_id)

        await self.cart_repository.clear_cart(cart.id)

        cart = await self.cart_repository.get_by_user_id(user_id)

        if not cart:
            raise NotFoundException("Cart not found")

        return self._build_cart_response(cart)

    @staticmethod
    def _build_cart_response(cart: Cart) -> CartResponse:
        items: list[CartItemResponse] = []
        total_amount = Decimal("0.00")
        total_items = 0

        for item in cart.items:
            total_price = item.unit_price * item.quantity

            items.append(
                CartItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=total_price,
                )
            )

            total_amount += total_price
            total_items += item.quantity

        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=items,
            total_items=total_items,
            total_amount=total_amount,
        )
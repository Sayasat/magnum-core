from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cart.models import Cart, CartItem


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_by_user_id(self, user_id: UUID) -> Cart:
        cart = await self.get_by_user_id(user_id)

        if cart:
            return cart

        cart = Cart(user_id=user_id)

        self.session.add(cart)
        await self.session.flush()
        await self.session.refresh(cart)

        return cart

    async def get_item_by_id(self, item_id: UUID) -> CartItem | None:
        stmt = select(CartItem).where(CartItem.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_item_by_cart_and_product(
            self,
            *,
            cart_id: UUID,
            product_id: UUID,
    ) -> CartItem | None:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_item(
            self,
            *,
            cart_id: UUID,
            product_id: UUID,
            quantity: int,
            unit_price,
    ) -> CartItem:
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)

        return item

    async def update_item(self, item: CartItem) -> CartItem:
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: CartItem) -> None:
        await self.session.delete(item)
        await self.session.flush()

    async def clear_cart(self, cart_id: UUID) -> None:
        stmt = delete(CartItem).where(CartItem.cart_id == cart_id)
        await self.session.execute(stmt)
        await self.session.flush()


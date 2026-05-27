from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user
from app.modules.cart.dependencies import get_cart_service
from app.modules.cart.schemas import (
    AddCartItemRequest,
    CartResponse,
    UpdateCartItemRequest,
)
from app.modules.cart.service import CartService
from app.modules.users.models import User

router = APIRouter()


@router.get(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
async def get_cart(
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.get_cart(current_user.id)


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
async def add_item(
    data: AddCartItemRequest,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.add_item(
        user_id=current_user.id,
        data=data,
    )


@router.patch(
    "/items/{item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
async def update_item(
    item_id: UUID,
    data: UpdateCartItemRequest,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.update_item(
        user_id=current_user.id,
        item_id=item_id,
        data=data,
    )


@router.delete(
    "/items/{item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
async def remove_item(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.remove_item(
        user_id=current_user.id,
        item_id=item_id,
    )


@router.delete(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return await service.clear_cart(current_user.id)
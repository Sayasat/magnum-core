from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.orders.schemas import OrderListResponse, OrderResponse
from app.modules.orders.service import OrderService
from app.modules.orders.dependencies import get_order_service
from app.modules.users.enums import UserRole
from app.modules.users.models import User

router = APIRouter()


@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def checkout(
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    order = await service.checkout(current_user.id)
    return OrderResponse.model_validate(order)


@router.get(
    "",
    response_model=OrderListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_my_orders(
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    orders = await service.list_user_orders(current_user.id)

    return OrderListResponse(
        items=[OrderResponse.model_validate(order) for order in orders],
        total=len(orders),
    )


@router.get(
    "/admin",
    response_model=OrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def list_all_orders(
    service: OrderService = Depends(get_order_service),
):
    orders = await service.list_all_orders()

    return OrderListResponse(
        items=[OrderResponse.model_validate(order) for order in orders],
        total=len(orders),
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    order = await service.get_user_order(
        user_id=current_user.id,
        order_id=order_id,
        is_admin=current_user.role == UserRole.ADMIN,
    )

    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    order = await service.cancel_order(
        user_id=current_user.id,
        order_id=order_id,
        is_admin=current_user.role == UserRole.ADMIN,
    )

    return OrderResponse.model_validate(order)
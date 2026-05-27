from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.orders.schemas import OrderListResponse, OrderResponse
from app.modules.orders.service import OrderService
from app.modules.orders.dependencies import get_order_service
from app.modules.users.enums import UserRole
from app.modules.users.models import User
from app.shared.pagination import PaginationParams, build_pagination_meta

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
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    orders, total = await service.list_user_orders(
        user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return OrderListResponse(
        items=[OrderResponse.model_validate(order) for order in orders],
        meta=build_pagination_meta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
        ),
    )


@router.get(
    "/admin",
    response_model=OrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def list_all_orders(
    pagination: PaginationParams = Depends(),
    service: OrderService = Depends(get_order_service),
):
    orders, total = await service.list_all_orders(
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return OrderListResponse(
        items=[OrderResponse.model_validate(order) for order in orders],
        meta=build_pagination_meta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
        ),
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

@router.post(
    "/{order_id}/complete",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def complete_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
):
    order = await service.complete_order(order_id)
    return OrderResponse.model_validate(order)
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user
from app.modules.payments.dependencies import get_payment_service
from app.modules.payments.schemas import PaymentResponse
from app.modules.payments.service import PaymentService
from app.modules.users.enums import UserRole
from app.modules.users.models import User

router = APIRouter()


@router.post(
    "/orders/{order_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_for_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    payment = await service.create_payment_for_order(
        user_id=current_user.id,
        order_id=order_id,
        is_admin=current_user.role == UserRole.ADMIN,
    )

    return PaymentResponse.model_validate(payment)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    payment = await service.get_payment(
        user_id=current_user.id,
        payment_id=payment_id,
        is_admin=current_user.role == UserRole.ADMIN,
    )

    return PaymentResponse.model_validate(payment)


@router.post(
    "/{payment_id}/success",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_payment_success(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    payment = await service.mark_payment_success(
        user_id=current_user.id,
        payment_id=payment_id,
        is_admin=current_user.role == UserRole.ADMIN,
    )

    return PaymentResponse.model_validate(payment)


@router.post(
    "/{payment_id}/fail",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_payment_failed(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    payment = await service.mark_payment_failed(
        user_id=current_user.id,
        payment_id=payment_id,
        is_admin=current_user.role == UserRole.ADMIN,
    )

    return PaymentResponse.model_validate(payment)
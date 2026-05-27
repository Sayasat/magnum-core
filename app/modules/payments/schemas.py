from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.payments.enums import PaymentProvider, PaymentStatus


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    status: PaymentStatus
    provider: PaymentProvider
    amount: Decimal
    external_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
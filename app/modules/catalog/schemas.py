from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.shared.pagination import PaginationMeta


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int


class ProductCreate(BaseModel):
    category_id: UUID
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0)
    sku: str = Field(min_length=2, max_length=100)
    stock_quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    category_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    sku: str | None = Field(default=None, min_length=2, max_length=100)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: UUID
    category_id: UUID
    name: str
    slug: str
    description: str | None
    price: Decimal
    sku: str
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    meta: PaginationMeta
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.catalog.dependencies import get_category_service, get_product_service
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.modules.catalog.service import CategoryService, ProductService
from app.modules.auth.dependencies import require_admin
from app.shared.pagination import PaginationParams, build_pagination_meta

router = APIRouter()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)],)
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    category = await service.create_category(data)
    return CategoryResponse.model_validate(category)


@router.get("/categories", response_model=CategoryListResponse, status_code=status.HTTP_200_OK,)
async def list_categories(service: CategoryService = Depends(get_category_service),):
    categories = await service.list_categories()
    return CategoryListResponse(items=categories,total=len(categories),)


@router.patch("/categories/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK,
              dependencies=[Depends(require_admin)],)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    category = await service.update_category(category_id, data)
    return CategoryResponse.model_validate(category)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)],)
async def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    product = await service.create_product(data)
    return ProductResponse.model_validate(product)


@router.get("/products", response_model=ProductListResponse, status_code=status.HTTP_200_OK,)
async def list_products(
    search: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    pagination: PaginationParams = Depends(),
    service: ProductService = Depends(get_product_service),
):
    products, total = await service.list_products(
        search=search,
        category_id=category_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return ProductListResponse(
        items=products,
        meta=build_pagination_meta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
        ),
    )


@router.get("/products/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK,)
async def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    return await service.get_product_by_id(product_id)


@router.patch("/products/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK,
              dependencies=[Depends(require_admin)],)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    product = await service.update_product(product_id, data)
    return ProductResponse.model_validate(product)
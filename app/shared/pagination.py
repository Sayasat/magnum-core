from math import ceil

from pydantic import BaseModel
from fastapi import Query


class PaginationParams:
    def __init__(
            self,
            page: int = Query(default=1, ge=1),
            limit: int = Query(default=20, ge=1, le=100),
    ):
        self.page = page
        self.limit = limit

    @property
    def offset(self) -> int:
        return (self.page-1)*self.limit

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int

def build_pagination_meta(*, page: int, limit: int, total: int,) -> PaginationMeta:
    pages = ceil(total / limit) if total > 0 else 0
    return PaginationMeta(page=page, limit=limit, total=total, pages=pages)

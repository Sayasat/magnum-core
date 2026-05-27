from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["Catalog"])

@api_router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "magnum-go"
    }

@api_router.get("/health/db")
async def health_db_check(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": result.scalar_one(),
    }

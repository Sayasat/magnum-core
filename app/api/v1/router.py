from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "magnum-go"
    }

@router.get("/health/db")
async def health_db_check(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": result.scalar_one(),
    }

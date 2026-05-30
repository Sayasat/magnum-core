from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest
from app.modules.auth.service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, service: AuthService = Depends(get_auth_service),):
    return await service.register(data)


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service),):
    return await service.login(data)
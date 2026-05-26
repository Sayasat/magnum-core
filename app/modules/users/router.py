from fastapi import APIRouter, Depends, status

from app.modules.users.dependencies import get_user_service
from app.modules.users.schemas import UserCreate, UserListResponse, UserResponse
from app.modules.users.service import UserService

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    user = await service.create_user(data)
    return UserResponse.model_validate(user)

@router.get("", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users(service: UserService = Depends(get_user_service)):
    users = await service.list_users()
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=len(users)
    )
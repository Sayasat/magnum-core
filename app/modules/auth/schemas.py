from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    user: UserResponse
    token: TokenResponse
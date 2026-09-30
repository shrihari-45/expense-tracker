from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: Optional[str] = Field(default=None, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: str = Field(..., description="Unique user UUID")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(default=None, description="User full name")
    created_at: Optional[str] = Field(default=None, description="Account creation timestamp")


class AuthResponse(BaseModel):
    token: str = Field(..., description="Bearer JWT access token")
    user: UserResponse = Field(..., description="Authenticated user profile")
    token_type: str = Field(default="bearer", description="Token type")


class TokenVerifyResponse(BaseModel):
    valid: bool = Field(..., description="Whether the token is valid")
    user: Optional[UserResponse] = Field(default=None, description="Verified user details")

"""
User-related Pydantic schemas
"""
# Third-party imports
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """Schema for user response data"""
    id: int

    class Config:
        from_attributes = True

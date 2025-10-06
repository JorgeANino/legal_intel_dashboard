"""
Authentication-related Pydantic schemas
"""
# Third-party imports
from pydantic import BaseModel, EmailStr

# Local application imports
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Login credentials schema"""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with tokens and user info"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    """Registration request schema"""

    email: EmailStr
    password: str
    full_name: str


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema"""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Registration response schema"""

    message: str
    email: str

"""
Authentication endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
)

router = APIRouter()


# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class RegisterResponse(BaseModel):
    message: str
    email: str


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint
    
    TODO: Implement actual user lookup from database
    """
    # TODO: Replace with actual database lookup
    # This is just a placeholder
    user_email = credentials.email
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_email})
    refresh_token = create_refresh_token(data={"sub": user_email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=RegisterResponse)
async def register(user_data: RegisterRequest):
    """
    Register new user
    
    TODO: Implement actual user creation in database
    """
    # TODO: Replace with actual database insertion
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    return {
        "message": "User registered successfully",
        "email": user_data.email
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    
    TODO: Implement token validation and refresh
    """
    # TODO: Validate refresh token and create new access token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )


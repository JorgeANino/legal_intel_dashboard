"""
Authentication endpoints
"""
# Local application imports
# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
)
from app.schemas.user import UserResponse


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.

    Args:
        credentials: User email and password.
        db: Database session dependency.

    Returns:
        LoginResponse with access token, refresh token, and user info.

    Raises:
        HTTPException: 401 if credentials are invalid.

    Example:
        POST /api/v1/auth/login
        {
            "email": "test@example.com",
            "password": "testpassword123"
        }
    """
    # Look up user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create tokens with user ID as subject
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """
    Get current user information from session.

    For now, returns the test user since we have single-user mode.
    In production, this would extract user ID from JWT token.

    Args:
        db: Database session dependency.

    Returns:
        UserResponse with current user information.

    Raises:
        HTTPException: 404 if user not found.

    Example:
        GET /api/v1/auth/me
        Headers: Authorization: Bearer <token>
    """
    # For single-user mode, return user with ID 1
    result = await db.execute(select(User).where(User.id == 1))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)

"""
User management endpoints (Simplified for demo)

Note: This is a minimal implementation for the coding challenge.
All documents use user_id=1 (mock user) since auth is optional.
For production, connect to database via app.models.user.
"""

# Local application imports
# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserBase, UserCreate, UserResponse


router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users (Protected - requires JWT token)

    Returns paginated list of users from database.

    Authorization: Bearer <JWT token>
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return list(users)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (Protected - requires JWT token)

    Returns user details if found. Users can only view their own profile
    unless they are superusers.

    Authorization: Bearer <JWT token>
    """
    # Check if user is requesting their own data or is a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create new user

    Note: Password hashing should be added for production.
    """
    # Local application imports
    from app.models.user import User

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user (password stored as-is for demo; use hashing in production)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=user_data.password,  # In production: hash this!
        is_active=user_data.is_active,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user details (Protected - requires JWT token)

    Updates email, full_name, and is_active status.
    Users can only update their own profile unless they are superusers.

    Authorization: Bearer <JWT token>
    """
    # Check if user is updating their own data or is a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
        )

    # Update fields
    user.email = user_data.email
    user.full_name = user_data.full_name
    user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Delete user (Protected - requires JWT token, admin only)

    Removes user from database.
    Note: In production, consider soft-delete to preserve data integrity.

    Authorization: Bearer <JWT token>
    Requires: Superuser role
    """
    # Only superusers can delete users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can delete users"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
        )

    await db.delete(user)
    await db.commit()

    return None

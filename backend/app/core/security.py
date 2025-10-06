"""
Security utilities for authentication and authorization
"""
# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT refresh token

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """
    Decode and verify JWT token

    Args:
        token: JWT token to decode

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# Bearer token security scheme
security = HTTPBearer()


async def get_current_user_from_token(token: str, db: AsyncSession):
    """
    Extract and validate user from JWT token

    Args:
        token: JWT token string
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Import here to avoid circular dependency
    # Local application imports
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception

        # Extract user_id from token and convert to int
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception

        try:
            user_id: int = int(user_id_raw)
        except (ValueError, TypeError):
            raise credentials_exception

        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

        return user

    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Dependency to get current authenticated user from JWT token

    NOTE: This dependency requires database access. Each endpoint using this
    must also include `db: AsyncSession = Depends(get_db)` parameter.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Import here to avoid circular dependency
    # Local application imports
    from app.core.database import AsyncSessionLocal
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = decode_token(credentials.credentials)
        if payload is None:
            raise credentials_exception

        # Extract user_id from token and convert to int
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception

        # Ensure user_id is an integer (JWT may store it as string)
        try:
            user_id: int = int(user_id_raw)
        except (ValueError, TypeError):
            raise credentials_exception

        # Create a new database session for auth validation
        async with AsyncSessionLocal() as db:
            # Get user from database
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if user is None:
                raise credentials_exception

            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

            return user

    except JWTError:
        raise credentials_exception

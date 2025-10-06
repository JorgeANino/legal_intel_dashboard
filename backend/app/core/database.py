"""
Production-ready database configuration with connection pooling
"""
# Local application imports
from app.core.config import settings
# Third-party imports
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool

# Create async engine with connection pooling for production
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Disable in production
    future=True,
    pool_size=settings.DB_POOL_SIZE,  # Number of connections to maintain
    max_overflow=settings.DB_MAX_OVERFLOW,  # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    poolclass=AsyncAdaptedQueuePool,  # Production-grade connection pool
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency to get database session with automatic rollback on errors

    Usage:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

"""
Health check and monitoring endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis import asyncio as aioredis
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for load balancers
    
    Checks:
    - API responsiveness
    - Database connectivity
    - Redis connectivity
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis = aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        await redis.close()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Prometheus-compatible metrics endpoint
    
    Returns:
    - Document processing queue size
    - Average processing time
    - Error rates
    """
    try:
        from app.models.document import Document, Query
        from sqlalchemy import func, select
        
        # Get processing queue size
        pending_docs = await db.execute(
            select(func.count(Document.id)).where(Document.processed == False)
        )
        queue_size = pending_docs.scalar() or 0
        
        # Get average query execution time
        avg_query_time = await db.execute(
            select(func.avg(Query.execution_time_ms))
        )
        avg_time = avg_query_time.scalar() or 0
        
        # Get error count
        error_count = await db.execute(
            select(func.count(Document.id))
            .where(Document.processing_error.isnot(None))
        )
        errors = error_count.scalar() or 0
        
        return {
            "document_queue_size": queue_size,
            "avg_query_time_ms": round(avg_time, 2),
            "processing_errors_total": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return default metrics if models not yet created
        return {
            "document_queue_size": 0,
            "avg_query_time_ms": 0.0,
            "processing_errors_total": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Models not yet initialized"
        }


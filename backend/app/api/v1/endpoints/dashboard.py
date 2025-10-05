"""
Dashboard statistics endpoint
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.document import DashboardStats
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics
    
    Returns aggregated counts of:
    - Agreement types
    - Jurisdictions
    - Industries
    - Geographies
    - Total documents and pages
    """
    service = DashboardService()
    user_id = 1  # Mock user_id
    
    stats = await service.get_dashboard_stats(user_id, db)
    return stats


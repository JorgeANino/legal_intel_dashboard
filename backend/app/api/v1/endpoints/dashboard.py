"""
Dashboard statistics endpoint
"""
# Local application imports
# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.document import DashboardStats
from app.services.dashboard_service import DashboardService


router = APIRouter()


@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics (Protected - requires JWT token)

    Returns aggregated counts of:
    - Agreement types
    - Jurisdictions
    - Industries
    - Geographies
    - Total documents and pages

    Authorization: Bearer <JWT token>
    """
    service = DashboardService()

    try:
        stats = await service.get_dashboard_stats(current_user.id, db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

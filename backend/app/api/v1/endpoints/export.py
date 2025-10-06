"""
Export endpoints for CSV and PDF generation
"""
# Standard library imports
from datetime import datetime

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.document import DashboardExportRequest, ExportRequest
from app.services.export_service import ExportService


router = APIRouter()


@router.post("/query-results/csv")
async def export_query_results_csv(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export query results as CSV (Protected - requires JWT token)

    Returns a CSV file with query results including all metadata fields.

    Authorization: Bearer <JWT token>
    """
    service = ExportService()

    try:
        csv_data = await service.export_query_results_csv(request, db)

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename or 'query-results'}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-results/pdf")
async def export_query_results_pdf(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export query results as PDF (Protected - requires JWT token)

    Returns a formatted PDF report with query results in a table format.

    Authorization: Bearer <JWT token>
    """
    service = ExportService()

    try:
        pdf_data = await service.export_query_results_pdf(request, db)

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename or 'query-results'}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard-report/pdf")
async def export_dashboard_report_pdf(
    request: DashboardExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export dashboard statistics as PDF report (Protected - requires JWT token)

    Returns a comprehensive PDF report with dashboard statistics,
    including charts if requested.

    Authorization: Bearer <JWT token>
    """
    service = ExportService()

    try:
        pdf_data = await service.export_dashboard_report_pdf(request, db)

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=dashboard-report-{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

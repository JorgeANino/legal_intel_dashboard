"""
Export service for generating CSV and PDF reports
"""
# Standard library imports
import csv
import io
from datetime import datetime
from typing import Any

# Local application imports
from app.schemas.document import DashboardStats, ExportRequest, QueryResponse
from app.services.dashboard_service import DashboardService
from app.services.query_service import QueryService
# Third-party imports
from fastapi import HTTPException
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.ext.asyncio import AsyncSession


class ExportService:
    """Service for exporting query results and dashboard reports"""

    def __init__(self):
        self.query_service = QueryService()
        self.dashboard_service = DashboardService()

    async def export_query_results_csv(self, request: ExportRequest, db: AsyncSession) -> str:
        """
        Export query results as CSV
        """
        try:
            # Execute query
            results = await self.query_service.execute_query(
                question=request.question,
                user_id=request.user_id,
                db=db,
                max_results=request.max_results or 1000,
                filters=request.filters.dict() if request.filters else None
            )

            # Convert to CSV
            csv_data = self._convert_to_csv(results["results"])
            return csv_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")

    async def export_query_results_pdf(self, request: ExportRequest, db: AsyncSession) -> bytes:
        """
        Export query results as PDF
        """
        try:
            # Execute query
            results = await self.query_service.execute_query(
                question=request.question,
                user_id=request.user_id,
                db=db,
                max_results=request.max_results or 1000,
                filters=request.filters.dict() if request.filters else None
            )

            # Generate PDF
            pdf_data = self._generate_pdf_report(results, request.template or "default")
            return pdf_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export PDF: {str(e)}")

    async def export_dashboard_report_pdf(self, request, db: AsyncSession) -> bytes:
        """
        Export dashboard statistics as PDF report
        """
        try:
            # Get dashboard stats
            stats = await self.dashboard_service.get_dashboard_stats(request.user_id, db)

            # Generate PDF report
            pdf_data = self._generate_dashboard_pdf(stats, request.include_charts)
            return pdf_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export dashboard report: {str(e)}")

    def _convert_to_csv(self, results: list[dict[str, Any]]) -> str:
        """Convert query results to CSV format"""
        if not results:
            return ""

        output = io.StringIO()
        
        # Get all possible headers
        headers = set(["document", "document_id"])
        for result in results:
            if "metadata" in result:
                headers.update(result["metadata"].keys())
        
        headers = sorted(list(headers))
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()

        for result in results:
            row = {
                "document": result.get("document", ""),
                "document_id": result.get("document_id", "")
            }
            
            if "metadata" in result:
                row.update(result["metadata"])
            
            writer.writerow(row)

        return output.getvalue()

    def _generate_pdf_report(self, results: dict[str, Any], template: str) -> bytes:
        """Generate PDF report using reportlab"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Query Results Report", title_style))
        story.append(Spacer(1, 12))

        # Query info
        query_info = f"<b>Query:</b> {results['question']}<br/>"
        query_info += f"<b>Total Results:</b> {results['total_results']}<br/>"
        query_info += f"<b>Execution Time:</b> {results['execution_time_ms']}ms<br/>"
        query_info += f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        story.append(Paragraph(query_info, styles['Normal']))
        story.append(Spacer(1, 20))

        # Results table
        if results["results"]:
            # Prepare table data
            table_data = [["Document", "Document ID"]]
            
            # Add metadata headers
            metadata_headers = set()
            for result in results["results"]:
                if "metadata" in result:
                    metadata_headers.update(result["metadata"].keys())
            
            table_data[0].extend(sorted(metadata_headers))
            
            # Add data rows
            for result in results["results"]:
                row = [result.get("document", ""), str(result.get("document_id", ""))]
                
                for header in sorted(metadata_headers):
                    value = ""
                    if "metadata" in result and header in result["metadata"]:
                        value = str(result["metadata"][header]) if result["metadata"][header] is not None else ""
                    row.append(value)
                
                table_data.append(row)

            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            story.append(table)
        else:
            story.append(Paragraph("No results found.", styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_dashboard_pdf(self, stats: DashboardStats, include_charts: bool) -> bytes:
        """Generate dashboard PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Legal Intel Dashboard Report", title_style))
        story.append(Spacer(1, 12))

        # Report info
        report_info = f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        report_info += f"<b>Total Documents:</b> {stats.total_documents}<br/>"
        report_info += f"<b>Processed Documents:</b> {stats.processed_documents}<br/>"
        report_info += f"<b>Total Pages:</b> {stats.total_pages:,}"
        
        story.append(Paragraph(report_info, styles['Normal']))
        story.append(Spacer(1, 20))

        # Agreement Types
        if stats.agreement_types:
            story.append(Paragraph("<b>Agreement Types</b>", styles['Heading2']))
            agreement_data = [["Agreement Type", "Count"]]
            for agreement_type, count in stats.agreement_types.items():
                agreement_data.append([agreement_type, str(count)])
            
            agreement_table = Table(agreement_data)
            agreement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(agreement_table)
            story.append(Spacer(1, 20))

        # Jurisdictions
        if stats.jurisdictions:
            story.append(Paragraph("<b>Jurisdictions</b>", styles['Heading2']))
            jurisdiction_data = [["Jurisdiction", "Count"]]
            for jurisdiction, count in stats.jurisdictions.items():
                jurisdiction_data.append([jurisdiction, str(count)])
            
            jurisdiction_table = Table(jurisdiction_data)
            jurisdiction_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(jurisdiction_table)
            story.append(Spacer(1, 20))

        # Industries
        if stats.industries:
            story.append(Paragraph("<b>Industries</b>", styles['Heading2']))
            industry_data = [["Industry", "Count"]]
            for industry, count in stats.industries.items():
                industry_data.append([industry, str(count)])
            
            industry_table = Table(industry_data)
            industry_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(industry_table)
            story.append(Spacer(1, 20))

        # Geographies
        if stats.geographies:
            story.append(Paragraph("<b>Geographies</b>", styles['Heading2']))
            geography_data = [["Geography", "Count"]]
            for geography, count in stats.geographies.items():
                geography_data.append([geography, str(count)])
            
            geography_table = Table(geography_data)
            geography_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(geography_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

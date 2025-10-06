"""
Dashboard service for generating statistics with caching
"""
# Standard library imports
from collections import Counter
from typing import Any

# Third-party imports
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.middleware.cache import cache_service
from app.models.document import Document, DocumentMetadata


class DashboardService:
    """Service for generating dashboard statistics with caching"""

    async def get_dashboard_stats(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        """
        Get aggregated dashboard statistics with Redis caching

        Returns:
            Dictionary with counts and aggregations

        Performance:
            - Results cached for 5 minutes
            - Cache invalidated on document upload
        """

        # Check cache first
        cache_key = f"dashboard_stats:user:{user_id}"
        cached_stats = await cache_service.get(cache_key)

        if cached_stats:
            return cached_stats

        # Get total documents
        total_docs_result = await db.execute(
            select(func.count(Document.id)).where(Document.user_id == user_id)
        )
        total_documents = total_docs_result.scalar() or 0

        # Get processed documents
        processed_docs_result = await db.execute(
            select(func.count(Document.id)).where(
                and_(Document.user_id == user_id, Document.processed is True)
            )
        )
        processed_documents = processed_docs_result.scalar() or 0

        # Get total pages
        total_pages_result = await db.execute(
            select(func.sum(Document.page_count)).where(Document.user_id == user_id)
        )
        total_pages = total_pages_result.scalar() or 0

        # Get all metadata for aggregation
        metadata_result = await db.execute(
            select(DocumentMetadata).join(Document).where(Document.user_id == user_id)
        )
        all_metadata = metadata_result.scalars().all()

        # Aggregate metadata
        agreement_types = Counter()
        jurisdictions = Counter()
        industries = Counter()
        geographies = Counter()

        for metadata in all_metadata:
            if metadata.agreement_type:
                agreement_types[metadata.agreement_type] += 1

            if metadata.governing_law:
                jurisdictions[metadata.governing_law] += 1

            if metadata.industry:
                industries[metadata.industry] += 1

            if metadata.geography:
                geographies[metadata.geography] += 1

        stats = {
            "total_documents": total_documents,
            "processed_documents": processed_documents,
            "total_pages": int(total_pages),
            "agreement_types": dict(agreement_types),
            "jurisdictions": dict(jurisdictions),
            "industries": dict(industries),
            "geographies": dict(geographies),
        }

        # Cache for 5 minutes
        await cache_service.set(cache_key, stats, ttl=300)

        return stats

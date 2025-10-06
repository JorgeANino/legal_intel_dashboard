"""
Mass interrogation query endpoint
"""
# Local application imports
# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.middleware.rate_limit import rate_limit_dependency
from app.models.user import User
from app.schemas.document import QueryRequest, QueryResponse, QuerySuggestionsResponse
from app.services.query_service import QueryService


router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_dependency),
):
    """
    Mass interrogation endpoint (Protected - requires JWT token)

    Execute natural language queries across all documents:
    - "Which agreements are governed by UAE law?"
    - "Show me all NDAs"
    - "List all technology contracts"

    Returns structured results matching the query

    Rate limit: 50 requests per minute

    Authorization: Bearer <JWT token>
    """
    service = QueryService()

    try:
        results = await service.execute_query(
            question=request.question,
            user_id=current_user.id,
            db=db,
            max_results=request.max_results or 50,
            page=request.page or 1,
            filters=request.filters,
            sort_by=request.sort_by or "relevance",
            sort_order=request.sort_order or "desc",
        )
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions", response_model=QuerySuggestionsResponse)
async def get_query_suggestions(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get query suggestions based on partial input (Protected - requires JWT token)

    Returns:
    - suggestions: Generated query suggestions
    - popular_queries: Popular queries from database
    - legal_terms: Common legal terminology
    - metadata_suggestions: Available filter options

    Authorization: Bearer <JWT token>
    """
    service = QueryService()

    try:
        suggestions = await service.get_query_suggestions(q, limit, db)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

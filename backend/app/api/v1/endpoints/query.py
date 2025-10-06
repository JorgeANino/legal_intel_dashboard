"""
Mass interrogation query endpoint
"""
# Local application imports
from app.core.database import get_db
from app.middleware.rate_limit import rate_limit_dependency
from app.schemas.document import QueryRequest, QueryResponse, QuerySuggestionsResponse
from app.services.query_service import QueryService
# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_dependency),
):
    """
    Mass interrogation endpoint

    Execute natural language queries across all documents:
    - "Which agreements are governed by UAE law?"
    - "Show me all NDAs"
    - "List all technology contracts"

    Returns structured results matching the query

    Rate limit: 50 requests per minute
    """
    service = QueryService()
    user_id = 1  # Mock user_id

    try:
        results = await service.execute_query(
            question=request.question, 
            user_id=user_id, 
            db=db, 
            max_results=request.max_results or 50,
            page=request.page or 1,
            filters=request.filters,
            sort_by=request.sort_by or "relevance",
            sort_order=request.sort_order or "desc"
        )
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions", response_model=QuerySuggestionsResponse)
async def get_query_suggestions(
    q: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get query suggestions based on partial input
    
    Returns:
    - suggestions: Generated query suggestions
    - popular_queries: Popular queries from database
    - legal_terms: Common legal terminology
    - metadata_suggestions: Available filter options
    """
    service = QueryService()
    
    try:
        suggestions = await service.get_query_suggestions(q, limit, db)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Mass interrogation query endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.document import QueryRequest, QueryResponse
from app.services.query_service import QueryService
from app.middleware.rate_limit import rate_limit_dependency

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_dependency)
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
            max_results=request.max_results
        )
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


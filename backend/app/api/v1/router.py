"""
API v1 Router - Legal Intel Dashboard
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, monitoring, documents, query, dashboard, users

api_router = APIRouter()

# Core endpoints for Legal Intel Dashboard
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# User management (simplified for demo - see users.py header notes)
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Note: Auth endpoints available but not required for this challenge
# Can be added via: from app.api.v1.endpoints import auth


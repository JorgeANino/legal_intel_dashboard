"""
API v1 Router - Legal Intel Dashboard
"""
# Local application imports
from app.api.v1.endpoints import (auth, dashboard, documents, export, health,
                                  monitoring, query, users, websocket)
# Third-party imports
from fastapi import APIRouter

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Core endpoints for Legal Intel Dashboard
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(export.router, prefix="/export", tags=["export"])

# WebSocket for real-time updates
api_router.include_router(websocket.router, tags=["websocket"])

# User management (simplified for demo - see users.py header notes)
api_router.include_router(users.router, prefix="/users", tags=["users"])

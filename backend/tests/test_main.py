"""
Basic tests for the main FastAPI application
"""
# Third-party imports
import pytest
# Local application imports
from app.main import app
from fastapi.testclient import TestClient


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_docs_endpoint(client):
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema(client):
    """Test that OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()

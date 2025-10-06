"""
Basic tests for the main FastAPI application
"""


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_docs_endpoint(client):
    """Test that API documentation is accessible"""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200


def test_openapi_schema(client):
    """Test that OpenAPI schema is accessible"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()

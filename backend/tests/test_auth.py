"""
Tests for authentication endpoints
"""
# Third-party imports
# Local application imports


def test_login_endpoint_exists(client):
    """Test that login endpoint exists and accepts POST requests"""
    response = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    # Should return 401 for wrong credentials, not 404
    assert response.status_code in [401, 422]  # 422 for validation errors


def test_me_endpoint_exists(client):
    """Test that /me endpoint exists"""
    response = client.get("/api/v1/auth/me")
    # Should return 401 for unauthenticated request, not 404
    assert response.status_code in [401, 403]


def test_login_validation(client):
    """Test login endpoint validation"""
    # Test missing email
    response = client.post("/api/v1/auth/login", json={"password": "testpassword123"})
    assert response.status_code == 422

    # Test missing password
    response = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422

    # Test invalid email format
    response = client.post(
        "/api/v1/auth/login", json={"email": "invalid-email", "password": "testpassword123"}
    )
    assert response.status_code == 422

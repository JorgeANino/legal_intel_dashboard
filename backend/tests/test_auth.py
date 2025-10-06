"""
Tests for authentication endpoints
"""


def test_login_endpoint_exists(client_no_auth):
    """Test that login endpoint exists and accepts POST requests"""
    response = client_no_auth.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    # Should return 401 for wrong credentials, not 404
    assert response.status_code in [401, 422]  # 422 for validation errors


def test_me_endpoint_exists(client_no_auth):
    """Test that /me endpoint exists"""
    response = client_no_auth.get("/api/v1/auth/me")
    # Should return 404 since no user with ID 1 exists in mock DB
    assert response.status_code in [401, 403, 404]


def test_login_validation(client_no_auth):
    """Test login endpoint validation"""
    # Test missing email
    response = client_no_auth.post("/api/v1/auth/login", json={"password": "testpassword123"})
    assert response.status_code == 422

    # Test missing password
    response = client_no_auth.post("/api/v1/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422

    # Test invalid email format
    response = client_no_auth.post(
        "/api/v1/auth/login", json={"email": "invalid-email", "password": "testpassword123"}
    )
    assert response.status_code == 422

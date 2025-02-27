"""Tests for authentication API endpoints."""

from unittest.mock import patch, MagicMock

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app.main import app
from app.auth.jwt import Token, User, create_access_token, get_current_active_user

client = TestClient(app)


@patch("app.auth.api.authenticate_user")
def test_login_for_access_token_valid(mock_authenticate_user):
    """Test login with valid credentials."""
    # Mock the authenticate_user function to return a valid user
    mock_authenticate_user.return_value = User(
        username="testuser",
        email="test@workflowforge.com",
        full_name="Test User",
        disabled=False
    )

    # Send a login request
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )

    # Verify the response
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Verify that authenticate_user was called with the correct parameters
    mock_authenticate_user.assert_called_once()


@patch("app.auth.api.authenticate_user")
def test_login_for_access_token_invalid(mock_authenticate_user):
    """Test login with invalid credentials."""
    # Mock the authenticate_user function to return False (invalid credentials)
    mock_authenticate_user.return_value = False

    # Send a login request
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )

    # Verify the response
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

    # Verify that authenticate_user was called with the correct parameters
    mock_authenticate_user.assert_called_once()


def test_read_users_me():
    """Test getting the current user's information."""
    # Create a mock user
    mock_user = User(
        username="testuser",
        email="test@workflowforge.com",
        full_name="Test User",
        disabled=False
    )

    # Override the dependency
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        # Send a request to get the current user's information
        response = client.get("/auth/users/me")

        # Verify the response
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@workflowforge.com"
        assert user_data["full_name"] == "Test User"
        assert user_data["disabled"] is False
    finally:
        # Restore the original dependency
        del app.dependency_overrides[get_current_active_user]


def test_get_users_me_no_token():
    """Test getting current user without a token."""
    # Make sure we don't have any overrides
    if get_current_active_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_active_user]

    # Send a request to get the current user's information without a token
    response = client.get("/auth/users/me")

    # Verify that the request is rejected
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

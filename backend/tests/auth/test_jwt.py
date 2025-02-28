"""Tests for JWT authentication module."""

import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth.jwt import (
    SECRET_KEY, ALGORITHM,
    verify_password, get_password_hash,
    authenticate_user, create_access_token,
    verify_token, get_current_user, fake_users_db
)


def test_verify_password():
    """Test password verification."""
    hashed_password = get_password_hash("testpassword")
    assert verify_password("testpassword", hashed_password)
    assert not verify_password("wrongpassword", hashed_password)


def test_get_password_hash():
    """Test password hashing."""
    hashed_password = get_password_hash("testpassword")
    assert hashed_password != "testpassword"
    assert isinstance(hashed_password, str)


def test_authenticate_user_valid():
    """Test user authentication with valid credentials."""
    user = authenticate_user(fake_users_db, "testuser", "testpassword")
    assert user is not False
    assert user.username == "testuser"


def test_authenticate_user_invalid_password():
    """Test user authentication with invalid password."""
    user = authenticate_user(fake_users_db, "testuser", "wrongpassword")
    assert user is None


def test_authenticate_user_invalid_username():
    """Test user authentication with invalid username."""
    user = authenticate_user(fake_users_db, "nonexistentuser", "testpassword")
    assert user is None


def test_create_access_token():
    """Test access token creation."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)

    # Decode the token and verify its contents
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_create_access_token_with_expiry():
    """Test access token creation with custom expiry."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=expires_delta)

    # Decode the token and verify its contents
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload


@patch("jose.jwt.decode")
def test_verify_token_valid(mock_decode):
    """Test token verification with a valid token."""
    # Mock the jwt.decode function to return a valid payload
    mock_decode.return_value = {
        "sub": "testuser",
        "exp": (datetime.utcnow() + timedelta(minutes=30)).timestamp()
    }

    # Create a dummy token
    token = "dummy_token"

    # Verify the token
    token_data = verify_token(token)
    assert token_data.username == "testuser"

    # Verify that jwt.decode was called with the correct parameters
    mock_decode.assert_called_once_with(
        token, SECRET_KEY, algorithms=[ALGORITHM])


def test_verify_token_expired():
    """Test token verification with an expired token."""
    # Create a token that expires immediately
    token = create_access_token(
        {"sub": "testuser"}, expires_delta=timedelta(seconds=-1))

    # Verify that an exception is raised for expired token
    with pytest.raises(HTTPException) as excinfo:
        verify_token(token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token has expired"


def test_verify_token_invalid():
    """Test token verification with an invalid token."""
    with pytest.raises(HTTPException) as excinfo:
        verify_token("invalid_token")

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"


@patch("app.auth.jwt.verify_token")
def test_get_current_user(mock_verify_token):
    """Test getting the current user from a token."""
    # Mock the verify_token function to return a token with username "testuser"
    from app.auth.jwt import TokenData
    mock_verify_token.return_value = TokenData(username="testuser")

    # Call get_current_user with a dummy token
    user = get_current_user("dummy_token")

    # Verify that the correct user is returned
    assert user.username == "testuser"
    assert user.email == "test@workflowforge.com"

    # Verify that verify_token was called with the correct token
    mock_verify_token.assert_called_once_with("dummy_token")

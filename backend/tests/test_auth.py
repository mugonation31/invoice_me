"""
Tests for JWT authentication module
"""
import pytest
from unittest.mock import MagicMock
from jose import jwt
from fastapi import HTTPException


def test_should_return_user_id_from_valid_jwt_token():
    """should return user_id from a valid JWT token"""
    # Arrange
    secret = "test-jwt-secret-key-for-testing-only"
    user_id = "user-uuid-12345"
    token = jwt.encode({"sub": user_id}, secret, algorithm="HS256")
    credentials = MagicMock()
    credentials.credentials = token

    # Act
    from auth import verify_token, get_current_user
    payload = verify_token(credentials)
    result = get_current_user(payload)

    # Assert
    assert result == user_id


def test_should_raise_401_for_invalid_jwt_token():
    """should raise 401 for an invalid JWT token"""
    # Arrange
    credentials = MagicMock()
    credentials.credentials = "invalid-token-string"

    # Act / Assert
    from auth import verify_token
    with pytest.raises(HTTPException) as exc_info:
        verify_token(credentials)

    assert exc_info.value.status_code == 401
    assert "Invalid authentication credentials" in exc_info.value.detail


def test_should_raise_401_when_sub_claim_is_missing():
    """should raise 401 when sub claim is missing from token"""
    # Arrange - token without 'sub' claim
    payload_without_sub = {"email": "test@example.com"}

    # Act / Assert
    from auth import get_current_user
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(payload_without_sub)

    assert exc_info.value.status_code == 401
    assert "User ID not found in token" in exc_info.value.detail

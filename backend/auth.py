"""
JWT Authentication module for verifying Supabase tokens
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import settings

# Security scheme for extracting Bearer token from headers
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token from Supabase and extract user information

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        dict: Decoded token payload containing user info

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    try:
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase tokens don't have aud claim
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(payload: dict = Depends(verify_token)) -> str:
    """
    Extract user ID from verified JWT token

    Args:
        payload: Decoded JWT payload from verify_token

    Returns:
        str: User ID (UUID)

    Raises:
        HTTPException: If user ID not found in token
    """
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    return user_id

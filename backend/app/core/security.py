"""Security Utilities for Authentication, JWT Token Handling, and Password Hashing.
Supports both python-jose and PyJWT seamlessly with graceful fallback.
"""

import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

# Graceful JWT import supporting both python-jose and pyjwt
try:
    from jose import jwt, JWTError
except ImportError:
    try:
        import jwt
        class JWTError(Exception):
            """Fallback JWTError when using PyJWT."""
            pass
    except ImportError:
        jwt = None
        class JWTError(Exception):
            pass

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.app.config import settings

# Password hashing context (pbkdf2_sha256)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2 Scheme for Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)


def hash_password(password: str) -> str:
    """Hash plaintext password securely using PBKDF2-SHA256."""
    return pwd_context.hash(password)


def get_password_hash(password: str) -> str:
    """Alias for hash_password to support standard FastAPI security conventions."""
    return hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against PBKDF2-SHA256 hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    if jwt is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT library (python-jose or PyJWT) is not available.",
        )
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    if isinstance(encoded_jwt, bytes):
        encoded_jwt = encoded_jwt.decode("utf-8")
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token."""
    if jwt is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT library (python-jose or PyJWT) is not available.",
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception as exc:
        # Catch both ExpiredSignatureError and any JWTError/InvalidTokenError
        err_type = type(exc).__name__
        if "Expired" in err_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT Token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate JWT credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """Dependency that extracts optional authenticated user payload."""
    if not token:
        return None
    return decode_access_token(token)

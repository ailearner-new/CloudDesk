"""Authentication and authorization for CloudDesk Support Platform."""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Role hierarchy: viewer < agent < admin
ROLE_LEVELS = {"viewer": 1, "agent": 2, "admin": 3}


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user id
    email: str
    role: str
    exp: int
    iat: int
    jti: str


class User(BaseModel):
    """Authenticated user."""
    id: str
    email: str
    role: str
    full_name: Optional[str] = None


security = HTTPBearer(auto_error=False)


def create_access_token(user: User, expires_hours: Optional[int] = None) -> str:
    """Create a JWT access token for a user."""
    settings = get_settings()
    expire_hours = expires_hours or settings.JWT_EXPIRY_HOURS
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=expire_hours)

    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "jti": str(uuid4()),
    }

    return jwt.encode(payload, settings.effective_jwt_secret, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.effective_jwt_secret,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    """Get the current authenticated user from the request."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = decode_token(credentials.credentials)

    return User(
        id=token_payload.sub,
        email=token_payload.email,
        role=token_payload.role,
    )


def require_role(required_role: str):
    """Dependency that requires a minimum role level."""
    required_level = ROLE_LEVELS.get(required_role, 0)

    async def role_checker(user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_LEVELS.get(user.role, 0)
        if user_level < required_level:
            logger.warning(
                "Role check failed",
                extra={
                    "user_id": user.id,
                    "user_role": user.role,
                    "required_role": required_role,
                    "user_level": user_level,
                    "required_level": required_level,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role or higher",
            )
        return user

    return role_checker


# Convenience dependencies
require_viewer = require_role("viewer")
require_agent = require_role("agent")
require_admin = require_role("admin")


def create_demo_token(email: str, role: str) -> str:
    """Create a demo token for testing."""
    user = User(
        id=f"demo-{role}-{email.split('@')[0]}",
        email=email,
        role=role,
        full_name=f"Demo {role.title()}",
    )
    return create_access_token(user)


# Demo user tokens (for testing without auth)
DEMO_TOKENS = {
    "admin@clouddesk.demo": create_demo_token("admin@clouddesk.demo", "admin"),
    "sam.agent@clouddesk.demo": create_demo_token("sam.agent@clouddesk.demo", "agent"),
    "vic.viewer@clouddesk.demo": create_demo_token("vic.viewer@clouddesk.demo", "viewer"),
}
"""Auth API routes for CloudDesk Support Platform."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel

from app.core.security import (
    get_current_user,
    create_access_token,
    decode_token,
    DEMO_TOKENS,
    User,
)
from app.schemas.common import LoginRequest, LoginResponse, RefreshResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


class DemoLoginRequest(BaseModel):
    """Demo login request."""
    email: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with email and password (demo mode)."""
    # In demo mode, accept any password for demo users
    demo_user = DEMO_TOKENS.get(request.email)
    if demo_user:
        # Decode the demo token to get user info
        payload = decode_token(demo_user)
        user = User(
            id=payload.sub,
            email=payload.email,
            role=payload.role,
            full_name=f"Demo {payload.role.title()}",
        )
        # Create fresh token
        access_token = create_access_token(user)
        return LoginResponse(
            access_token=access_token,
            expires_in=8 * 3600,
            user=UserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                full_name=user.full_name,
            ),
        )

    # For non-demo users, would validate against database
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )


@router.post("/demo-login", response_model=LoginResponse)
async def demo_login(request: DemoLoginRequest):
    """Login as a demo user (no password required)."""
    demo_user = DEMO_TOKENS.get(request.email)
    if not demo_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo user not found",
        )

    payload = decode_token(demo_user)
    user = User(
        id=payload.sub,
        email=payload.email,
        role=payload.role,
        full_name=f"Demo {payload.role.title()}",
    )
    access_token = create_access_token(user)

    return LoginResponse(
        access_token=access_token,
        expires_in=8 * 3600,
        user=UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name,
        ),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    access_token = create_access_token(current_user)
    return RefreshResponse(
        access_token=access_token,
        expires_in=8 * 3600,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
    )
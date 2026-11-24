"""Settings API routes for CloudDesk Support Platform."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user, require_admin, User
from app.schemas.common import SettingsResponse, SettingsUpdate
from app.core.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings_api(
    current_user: User = Depends(require_admin),
):
    """Get current settings (admin only)."""
    settings = get_settings()
    return SettingsResponse(
        approval_required_for_refunds=settings.APPROVAL_REQUIRED_FOR_REFUNDS,
        max_refund_without_approval=settings.MAX_REFUND_WITHOUT_APPROVAL,
        rate_limit_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        tool_timeout_seconds=settings.TOOL_TIMEOUT_SECONDS,
        vector_store=settings.VECTOR_STORE,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        llm_provider=settings.LLM_PROVIDER,
    )


@router.patch("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    current_user: User = Depends(require_admin),
):
    """Update settings (admin only)."""
    # In a real implementation, this would update environment variables or a config table
    # For now, return current settings
    settings = get_settings()
    return SettingsResponse(
        approval_required_for_refunds=settings.APPROVAL_REQUIRED_FOR_REFUNDS,
        max_refund_without_approval=settings.MAX_REFUND_WITHOUT_APPROVAL,
        rate_limit_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        tool_timeout_seconds=settings.TOOL_TIMEOUT_SECONDS,
        vector_store=settings.VECTOR_STORE,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        llm_provider=settings.LLM_PROVIDER,
    )
"""
Settings & privacy: account deletion (required by Google Play).
Export and other settings follow in Phase 16.
"""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_session
from app.api.routes.auth import clear_auth_cookies
from app.core.exceptions import BadRequestException
from app.core.security import verify_password
from app.models.auth import User
from app.models.resume import Resume
from app.services.storage import storage_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["Group 14: Settings & Privacy"])


class DeleteAccountRequest(BaseModel):
    password: str
    confirm: str  # must be the word DELETE, so one stray click can't erase an account


@router.get("", summary="Settings Module Status")
async def settings_status() -> Dict[str, str]:
    return {"module": "settings", "status": "operational", "phase": "Phase 16"}


@router.delete("/account", status_code=204, summary="Permanently delete my account and all my data")
async def delete_account(
    body: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Response:
    if body.confirm != "DELETE":
        raise BadRequestException("Type DELETE to confirm.")
    if not verify_password(body.password, current_user.password_hash):
        raise BadRequestException("That password is not correct.")

    user_id = current_user.id
    paths = list((await db.execute(select(Resume.storage_path).where(Resume.user_id == user_id))).scalars())

    # Every table that points at users uses ON DELETE CASCADE, so one delete removes all rows.
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()

    # Files go after the commit: a failed file delete must not keep the account alive.
    for path in paths:
        try:
            await storage_service.delete_file(path)
        except Exception:  # noqa: BLE001
            logger.warning("Could not delete stored file for a deleted account", exc_info=True)

    response = Response(status_code=204)
    clear_auth_cookies(response)
    return response

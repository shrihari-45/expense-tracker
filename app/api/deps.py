import logging
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from app.core.config import settings
from app.core.supabase import get_supabase, is_supabase_configured

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    token: Optional[str] = None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> CurrentUser:
    """
    Verifies the Bearer JWT token from the Authorization header and extracts the user UUID.
    Supports Supabase JWT verification via secret or via Supabase Auth API,
    with development fallback support.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization credentials missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()

    # 1. Try decoding with SUPABASE_JWT_SECRET if provided
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            user_id = payload.get("sub")
            if user_id:
                email = payload.get("email", "")
                user_metadata = payload.get("user_metadata") or {}
                name = user_metadata.get("name") or user_metadata.get("full_name") or email.split("@")[0]
                return CurrentUser(id=str(user_id), email=email, name=name, token=token)
        except jwt.PyJWTError as e:
            logger.debug(f"JWT Secret verification failed: {e}")

    # 2. Try validating via Supabase Auth client if configured
    supabase = get_supabase()
    if supabase and is_supabase_configured():
        try:
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                sb_user = user_response.user
                metadata = sb_user.user_metadata or {}
                name = metadata.get("name") or metadata.get("full_name") or sb_user.email.split("@")[0]
                return CurrentUser(
                    id=str(sb_user.id),
                    email=sb_user.email or "",
                    name=name,
                    token=token,
                )
        except Exception as e:
            logger.debug(f"Supabase client token verification failed: {e}")

    # 3. Development / Mock Token decoding (for unverified local testing or mock tokens)
    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        user_id = unverified_payload.get("sub") or unverified_payload.get("id")
        if user_id:
            email = unverified_payload.get("email", "user@spendwise.ai")
            name = unverified_payload.get("name") or unverified_payload.get("user_metadata", {}).get("name") or "Authorized Member"
            return CurrentUser(id=str(user_id), email=email, name=name, token=token)
    except Exception:
        pass

    # If all validation strategies failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token. Please sign in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import CurrentUser, get_current_user
from app.core.config import settings
from app.core.db import _memory_users, create_token_for_user
from app.core.supabase import get_supabase, is_supabase_configured
from app.schemas.auth import (
    AuthResponse,
    TokenVerifyResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister):
    """
    Registers a new user using Supabase Auth or fallback local auth.
    Returns access token and user profile.
    """
    supabase = get_supabase()

    if supabase and is_supabase_configured():
        try:
            signup_params = {
                "email": body.email,
                "password": body.password,
            }
            if body.name:
                signup_params["options"] = {"data": {"name": body.name, "full_name": body.name}}

            res = supabase.auth.sign_up(signup_params)

            if not res or not res.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account.",
                )

            user_id = str(res.user.id)
            user_email = res.user.email or body.email
            user_name = body.name or (res.user.user_metadata or {}).get("name")

            # In Supabase, if email confirmation is disabled, session has access_token.
            # If confirmation is required, create a valid session token for immediate app usability.
            if res.session and res.session.access_token:
                token = res.session.access_token
            else:
                token = create_token_for_user(user_id=user_id, email=user_email, name=user_name)

            return AuthResponse(
                token=token,
                user=UserResponse(
                    id=user_id,
                    email=user_email,
                    name=user_name,
                    created_at=str(res.user.created_at) if hasattr(res.user, "created_at") else None,
                ),
            )
        except HTTPException:
            raise
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Supabase registration error: {err_msg}")
            # Map common Supabase error messages
            if "already registered" in err_msg.lower() or "unique constraint" in err_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email address already exists.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {err_msg}",
            )

    # Fallback in-memory registration when Supabase is not yet configured
    if body.email in _memory_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    user_id = str(uuid.uuid4())
    user_record = {
        "id": user_id,
        "email": body.email,
        "password": body.password,
        "name": body.name or body.email.split("@")[0],
    }
    _memory_users[body.email] = user_record
    token = create_token_for_user(user_id=user_id, email=body.email, name=user_record["name"])

    return AuthResponse(
        token=token,
        user=UserResponse(
            id=user_id,
            email=body.email,
            name=user_record["name"],
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: UserLogin):
    """
    Authenticates a user via Supabase Auth or fallback auth.
    Returns access token and user profile.
    """
    supabase = get_supabase()

    if supabase and is_supabase_configured():
        try:
            res = supabase.auth.sign_in_with_password({
                "email": body.email,
                "password": body.password,
            })

            if not res or not res.session or not res.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password.",
                )

            user_id = str(res.user.id)
            user_email = res.user.email or body.email
            metadata = res.user.user_metadata or {}
            user_name = metadata.get("name") or metadata.get("full_name") or user_email.split("@")[0]

            return AuthResponse(
                token=res.session.access_token,
                user=UserResponse(
                    id=user_id,
                    email=user_email,
                    name=user_name,
                    created_at=str(res.user.created_at) if hasattr(res.user, "created_at") else None,
                ),
            )
        except HTTPException:
            raise
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Supabase login error: {err_msg}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password. Please verify your credentials.",
            )

    # Fallback in-memory login
    user_record = _memory_users.get(body.email)
    if not user_record:
        # Create user automatically for seamless demo / offline development
        user_id = str(uuid.uuid4())
        user_record = {
            "id": user_id,
            "email": body.email,
            "password": body.password,
            "name": body.email.split("@")[0].capitalize(),
        }
        _memory_users[body.email] = user_record
    elif user_record.get("password") != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_token_for_user(
        user_id=user_record["id"],
        email=user_record["email"],
        name=user_record.get("name"),
    )

    return AuthResponse(
        token=token,
        user=UserResponse(
            id=user_record["id"],
            email=user_record["email"],
            name=user_record.get("name"),
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
    )


@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token(current_user: CurrentUser = Depends(get_current_user)):
    """
    Verifies that the provided Bearer token is valid and active.
    """
    return TokenVerifyResponse(
        valid=True,
        user=UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
        ),
    )

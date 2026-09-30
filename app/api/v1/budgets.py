import logging
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import CurrentUser, get_current_user
from app.core.db import _memory_budgets
from app.core.supabase import get_authenticated_client, is_supabase_configured
from app.schemas.budget import BudgetCreate, BudgetResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=List[BudgetResponse])
@router.get("/", response_model=List[BudgetResponse])
async def list_budgets(current_user: CurrentUser = Depends(get_current_user)):
    """
    Retrieves all budget ceilings defined by the authenticated user.
    """
    supabase = get_authenticated_client(current_user.token)

    if supabase and is_supabase_configured():
        try:
            res = supabase.table("budgets").select("*").eq("user_id", current_user.id).execute()
            if res.data:
                return res.data
        except Exception as e:
            logger.warning(f"Supabase budget query failed ({e}), using local store.")

    # Fallback in-memory
    user_budgets = [
        b for b in _memory_budgets
        if b.get("user_id") == current_user.id or b.get("user_id") == "demo-user-id"
    ]
    return user_budgets


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_200_OK)
@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_200_OK)
async def upsert_budget(
    body: BudgetCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Upserts a budget ceiling limit for a category.
    If a limit already exists for this category, it is updated; otherwise a new record is created.
    """
    supabase = get_authenticated_client(current_user.token)
    now_iso = datetime.now(timezone.utc).isoformat()

    if supabase and is_supabase_configured():
        try:
            check = (
                supabase.table("budgets")
                .select("*")
                .eq("user_id", current_user.id)
                .eq("category", body.category)
                .execute()
            )

            if check.data and len(check.data) > 0:
                existing_id = check.data[0]["id"]
                res = (
                    supabase.table("budgets")
                    .update({"limit": body.limit, "updated_at": now_iso})
                    .eq("id", existing_id)
                    .execute()
                )
                if res.data:
                    return res.data[0]
            else:
                payload = {
                    "user_id": current_user.id,
                    "category": body.category,
                    "limit": body.limit,
                    "created_at": now_iso,
                    "updated_at": now_iso,
                }
                res = supabase.table("budgets").insert(payload).execute()
                if res.data:
                    return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase budget upsert failed ({e}), using local store.")

    # Fallback in-memory
    for b in _memory_budgets:
        if (b.get("user_id") == current_user.id or b.get("user_id") == "demo-user-id") and b.get("category") == body.category:
            b["limit"] = body.limit
            b["updated_at"] = now_iso
            return b

    new_budget = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "category": body.category,
        "limit": body.limit,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    _memory_budgets.append(new_budget)
    return new_budget

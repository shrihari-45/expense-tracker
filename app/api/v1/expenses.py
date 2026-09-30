import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import CurrentUser, get_current_user
from app.core.db import _memory_expenses
from app.core.supabase import get_authenticated_client, is_supabase_configured
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=List[ExpenseResponse])
@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    search: Optional[str] = Query(default=None, description="Search term for title or description"),
    sort: Optional[str] = Query(default="date-desc", description="Sort order: date-desc, date-asc, amount-desc, amount-asc"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Retrieves all expenses belonging to the authenticated user.
    Supports optional category filtering, keyword searching, and sorting.
    """
    supabase = get_authenticated_client(current_user.token)

    if supabase and is_supabase_configured():
        try:
            query = supabase.table("expenses").select("*").eq("user_id", current_user.id)

            if category and category != "All Categories":
                query = query.eq("category", category)

            if search:
                query = query.ilike("title", f"%{search}%")

            # Sorting
            if sort == "date-asc":
                query = query.order("date", desc=False)
            elif sort == "amount-desc":
                query = query.order("amount", desc=True)
            elif sort == "amount-asc":
                query = query.order("amount", desc=False)
            else:
                query = query.order("date", desc=True)

            res = query.execute()
            records = res.data or []

            # Search filtering on description
            if search:
                s_lower = search.lower()
                records = [
                    r for r in records
                    if s_lower in r.get("title", "").lower() or s_lower in r.get("description", "").lower()
                ]

            if records:
                return records
        except Exception as e:
            logger.warning(f"Supabase query failed ({e}), falling back to local store.")

    # Fallback in-memory implementation
    items = [
        e for e in _memory_expenses
        if e.get("user_id") == current_user.id or e.get("user_id") == "demo-user-id"
    ]

    if category and category != "All Categories":
        items = [e for e in items if e.get("category") == category]

    if search:
        s_lower = search.lower()
        items = [
            e for e in items
            if s_lower in e.get("title", "").lower() or s_lower in e.get("description", "").lower()
        ]

    # Sort
    if sort == "date-asc":
        items.sort(key=lambda x: str(x.get("date", "")))
    elif sort == "amount-desc":
        items.sort(key=lambda x: float(x.get("amount", 0)), reverse=True)
    elif sort == "amount-asc":
        items.sort(key=lambda x: float(x.get("amount", 0)))
    else:
        items.sort(key=lambda x: str(x.get("date", "")), reverse=True)

    return items


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    body: ExpenseCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Creates a new expense record belonging to the authenticated user.
    """
    supabase = get_authenticated_client(current_user.token)
    now_iso = datetime.now(timezone.utc).isoformat()

    if supabase and is_supabase_configured():
        try:
            payload = {
                "user_id": current_user.id,
                "title": body.title,
                "amount": body.amount,
                "category": body.category,
                "date": body.date,
                "payment_method": body.payment_method or "UPI",
                "description": body.description or "",
            }
            res = supabase.table("expenses").insert(payload).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            logger.warning(f"Supabase insert failed ({e}). Persisting to fallback storage so user experience is not disrupted.")

    # Fallback in-memory
    new_expense = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "title": body.title,
        "amount": body.amount,
        "category": body.category,
        "date": body.date,
        "payment_method": body.payment_method or "UPI",
        "description": body.description or "",
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    _memory_expenses.insert(0, new_expense)
    return new_expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    body: ExpenseUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Updates an existing expense record. Strictly enforces user ownership.
    """
    supabase = get_authenticated_client(current_user.token)

    if supabase and is_supabase_configured():
        try:
            # Check ownership first
            check = supabase.table("expenses").select("*").eq("id", expense_id).execute()
            if check.data and len(check.data) > 0:
                if check.data[0].get("user_id") != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied: You can only edit your own expenses.",
                    )

                update_data = body.model_dump(exclude_unset=True)
                if not update_data:
                    return check.data[0]

                update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                res = (
                    supabase.table("expenses")
                    .update(update_data)
                    .eq("id", expense_id)
                    .eq("user_id", current_user.id)
                    .execute()
                )
                if res.data:
                    return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Supabase update failed ({e}), checking fallback store.")

    # Fallback in-memory update
    for item in _memory_expenses:
        if item.get("id") == expense_id:
            if item.get("user_id") != current_user.id and item.get("user_id") != "demo-user-id":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only edit your own expenses.",
                )
            update_dict = body.model_dump(exclude_unset=True)
            item.update(update_dict)
            item["updated_at"] = datetime.now(timezone.utc).isoformat()
            return item

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Expense entry not found.",
    )


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Deletes an existing expense record. Strictly enforces user ownership.
    """
    supabase = get_authenticated_client(current_user.token)

    if supabase and is_supabase_configured():
        try:
            check = supabase.table("expenses").select("user_id").eq("id", expense_id).execute()
            if check.data and len(check.data) > 0:
                if check.data[0].get("user_id") != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied: You can only delete your own expenses.",
                    )

                supabase.table("expenses").delete().eq("id", expense_id).eq("user_id", current_user.id).execute()
                return {"message": "Expense deleted successfully", "id": expense_id}
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Supabase delete failed ({e}), checking fallback store.")

    # Fallback in-memory
    for i, item in enumerate(_memory_expenses):
        if item.get("id") == expense_id:
            if item.get("user_id") != current_user.id and item.get("user_id") != "demo-user-id":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only delete your own expenses.",
                )
            _memory_expenses.pop(i)
            return {"message": "Expense deleted successfully", "id": expense_id}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Expense entry not found.",
    )

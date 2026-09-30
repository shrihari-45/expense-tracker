import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import CurrentUser, get_current_user
from app.core.db import _memory_budgets, _memory_expenses
from app.core.supabase import get_supabase, is_supabase_configured
from app.schemas.ai import (
    CategorizeRequest,
    CategorizeResponse,
    ChatRequest,
    ChatResponse,
    InsightsResponse,
)
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Engine"])


async def _get_user_financial_context(user_id: str):
    """Helper to fetch current user's expenses and budgets."""
    supabase = get_supabase()

    if supabase and is_supabase_configured():
        try:
            exp_res = supabase.table("expenses").select("*").eq("user_id", user_id).execute()
            b_res = supabase.table("budgets").select("*").eq("user_id", user_id).execute()
            return exp_res.data or [], b_res.data or []
        except Exception as e:
            logger.error(f"Error querying financial context from Supabase: {e}")

    # Fallback in-memory
    expenses = [
        e for e in _memory_expenses
        if e.get("user_id") == user_id or e.get("user_id") == "demo-user-id"
    ]
    budgets = [
        b for b in _memory_budgets
        if b.get("user_id") == user_id or b.get("user_id") == "demo-user-id"
    ]
    return expenses, budgets


@router.post("/categorize", response_model=CategorizeResponse)
async def categorize_expense(body: CategorizeRequest):
    """
    Predicts transaction category (Food, Transport, Shopping, Bills, etc.)
    based on the transaction title or vendor name.
    """
    query_text = body.query
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction title or text is required for categorization.",
        )
    return AIService.predict_category(query_text)


@router.post("/insights", response_model=InsightsResponse)
async def get_insights(current_user: CurrentUser = Depends(get_current_user)):
    """
    Computes real-time financial insights, including:
    - Anomalies and outlier expenditures
    - Largest category spikes
    - Budget guardrails & threshold overruns
    - Actionable saving suggestions
    """
    expenses, budgets = await _get_user_financial_context(current_user.id)
    return AIService.generate_financial_insights(expenses=expenses, budgets=budgets)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    body: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Answers natural language financial inquiries within the context of the user's
    recorded ledger and budget ceilings.
    """
    expenses, budgets = await _get_user_financial_context(current_user.id)
    return await AIService.process_chat(
        question=body.text,
        expenses=expenses,
        budgets=budgets,
    )

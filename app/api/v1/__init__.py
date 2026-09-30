from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.budgets import router as budgets_router
from app.api.v1.ai import router as ai_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(expenses_router)
api_v1_router.include_router(budgets_router)
api_v1_router.include_router(ai_router)

__all__ = ["api_v1_router"]

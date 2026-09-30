import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import jwt
from app.core.config import settings
from app.core.supabase import get_supabase, is_supabase_configured

logger = logging.getLogger(__name__)

# In-memory store for fallback / local development when Supabase credentials are not yet configured
_memory_users: Dict[str, Dict[str, Any]] = {}
_memory_expenses: List[Dict[str, Any]] = [
    {
        "id": "e1-demo-uuid-001",
        "user_id": "demo-user-id",
        "title": "Grocery Supermarket",
        "amount": 3450.0,
        "category": "Groceries",
        "date": "2026-03-24",
        "payment_method": "UPI",
        "description": "Weekly grocery restocking",
        "created_at": "2026-03-24T10:00:00Z",
    },
    {
        "id": "e2-demo-uuid-002",
        "user_id": "demo-user-id",
        "title": "Uber ride to office",
        "amount": 420.0,
        "category": "Transport",
        "date": "2026-03-25",
        "payment_method": "Credit Card",
        "description": "Morning commute",
        "created_at": "2026-03-25T09:30:00Z",
    },
    {
        "id": "e3-demo-uuid-003",
        "user_id": "demo-user-id",
        "title": "Electricity & Power Bill",
        "amount": 2100.0,
        "category": "Bills",
        "date": "2026-03-22",
        "payment_method": "Bank Transfer",
        "description": "Monthly utility bill",
        "created_at": "2026-03-22T14:15:00Z",
    },
    {
        "id": "e4-demo-uuid-004",
        "user_id": "demo-user-id",
        "title": "Weekend Dinner at Bistro",
        "amount": 2800.0,
        "category": "Food",
        "date": "2026-03-20",
        "payment_method": "UPI",
        "description": "Family dinner",
        "created_at": "2026-03-20T20:45:00Z",
    },
    {
        "id": "e5-demo-uuid-005",
        "user_id": "demo-user-id",
        "title": "Online Electronics Store",
        "amount": 6200.0,
        "category": "Shopping",
        "date": "2026-03-18",
        "payment_method": "Credit Card",
        "description": "Mechanical keyboard and mousepad",
        "created_at": "2026-03-18T16:00:00Z",
    },
]

_memory_budgets: List[Dict[str, Any]] = [
    {"id": "b1-demo-uuid", "user_id": "demo-user-id", "category": "Food", "limit": 7000.0},
    {"id": "b2-demo-uuid", "user_id": "demo-user-id", "category": "Shopping", "limit": 5000.0},
    {"id": "b3-demo-uuid", "user_id": "demo-user-id", "category": "Transport", "limit": 3000.0},
    {"id": "b4-demo-uuid", "user_id": "demo-user-id", "category": "Bills", "limit": 4000.0},
]


def create_token_for_user(user_id: str, email: str, name: Optional[str] = None) -> str:
    """Creates a JWT token signed with SUPABASE_JWT_SECRET or standard HS256 secret."""
    secret = settings.SUPABASE_JWT_SECRET or "spendwise-secret-key-fallback-32chars"
    payload = {
        "sub": user_id,
        "email": email,
        "user_metadata": {"name": name, "full_name": name},
        "aud": "authenticated",
        "role": "authenticated",
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")

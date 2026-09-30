from typing import Optional
from pydantic import BaseModel, Field


class ExpenseBase(BaseModel):
    title: str = Field(..., min_length=1, description="Expense title / payee / vendor")
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    category: str = Field(..., description="Expense category (Food, Shopping, etc.)")
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    payment_method: Optional[str] = Field(default="UPI", description="Payment method used")
    description: Optional[str] = Field(default="", description="Additional details or notes")


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    amount: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
    date: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: str = Field(..., description="Unique expense UUID")
    user_id: str = Field(..., description="Owner user UUID")
    created_at: Optional[str] = Field(default=None, description="Record creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Record update timestamp")

    model_config = {"from_attributes": True}

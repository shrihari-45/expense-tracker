from typing import Optional
from pydantic import BaseModel, Field


class BudgetBase(BaseModel):
    category: str = Field(..., description="Target spending category")
    limit: float = Field(..., gt=0, description="Monthly ceiling limit for the category")


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: str = Field(..., description="Unique budget UUID or ID")
    user_id: str = Field(..., description="Owner user UUID")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")

    model_config = {"from_attributes": True}

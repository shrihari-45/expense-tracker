from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class CategorizeRequest(BaseModel):
    text: Optional[str] = Field(default=None, description="Title or transaction description to categorize")
    title: Optional[str] = Field(default=None, description="Alternative field for transaction title")

    @model_validator(mode="after")
    def validate_text_or_title(self):
        query_text = (self.text or self.title or "").strip()
        if not query_text:
            raise ValueError("Either 'text' or 'title' must be provided and non-empty.")
        return self

    @property
    def query(self) -> str:
        return (self.text or self.title or "").strip()


class CategorizeResponse(BaseModel):
    category: str = Field(..., description="Predicted expense category")
    confidence: float = Field(default=0.95, description="Confidence score from 0.0 to 1.0")
    reasoning: Optional[str] = Field(default=None, description="Brief rationale for the categorization")


class InsightItem(BaseModel):
    type: str = Field(..., description="Insight type ('alert' for spikes/overruns, 'tip' for recommendations)")
    message: str = Field(..., description="Descriptive text of the insight")
    category: Optional[str] = Field(default=None, description="Related category if applicable")
    metric: Optional[str] = Field(default=None, description="Associated metric or value")


class InsightsResponse(BaseModel):
    insights: List[InsightItem] = Field(default_factory=list, description="Computed financial insights and recommendations")
    total_expenses: Optional[float] = Field(default=None, description="Total computed expenses")
    top_category: Optional[str] = Field(default=None, description="Category with highest expenditure")
    anomalies_count: Optional[int] = Field(default=0, description="Number of anomalous expenditures detected")


class ChatRequest(BaseModel):
    question: Optional[str] = Field(default=None, description="Natural language question about finances")
    query: Optional[str] = Field(default=None, description="Alternative field for query")

    @model_validator(mode="after")
    def validate_question(self):
        q = (self.question or self.query or "").strip()
        if not q:
            raise ValueError("Either 'question' or 'query' must be provided.")
        return self

    @property
    def text(self) -> str:
        return (self.question or self.query or "").strip()


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Context-aware natural language answer")
    suggested_actions: Optional[List[str]] = Field(default=None, description="Follow-up questions or actions")

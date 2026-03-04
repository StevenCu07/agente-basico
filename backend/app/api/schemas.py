from typing import Literal

from pydantic import BaseModel, Field


ToolName = Literal["resumir", "quiz", "flashcards", "plan", "buscar", "cost"]


class ChatRequest(BaseModel):
    user_token: str = Field(..., min_length=3)
    message: str = Field(..., min_length=1)
    tool: ToolName | None = None
    context: str | None = None


class ToolTextRequest(BaseModel):
    user_token: str = Field(..., min_length=3)
    text: str = Field(..., min_length=1)


class SummaryRequest(ToolTextRequest):
    max_words: int = Field(default=140, ge=40, le=300)


class QuizRequest(ToolTextRequest):
    questions: int = Field(default=5, ge=1, le=15)


class FlashcardsRequest(ToolTextRequest):
    cards: int = Field(default=6, ge=2, le=20)


class StudyPlanRequest(BaseModel):
    user_token: str = Field(..., min_length=3)
    topics: list[str] = Field(default_factory=list)
    available_hours_per_week: int = Field(default=8, ge=1, le=80)
    target_date: str = Field(..., min_length=10, max_length=10)


class SearchRequest(BaseModel):
    user_token: str = Field(..., min_length=3)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class CostEstimateRequest(BaseModel):
    daily_interactions: int = Field(..., ge=0, le=10000)
    avg_tokens_in: int = Field(..., ge=0, le=500000)
    avg_tokens_out: int = Field(..., ge=0, le=500000)
    days: int = Field(default=30, ge=1, le=366)


class DocumentCreateRequest(BaseModel):
    user_token: str = Field(..., min_length=3)
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


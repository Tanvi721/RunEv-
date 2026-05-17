from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    request_id: int
    score: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=1000)


class RatingResponse(BaseModel):
    id: int
    request_id: int
    user_id: int
    provider_id: int
    score: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProviderRatingSummary(BaseModel):
    provider_id: int
    average_rating: Optional[float] = None
    rating_count: int

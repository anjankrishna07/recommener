from pydantic import BaseModel, Field
from typing import Optional


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, example="space exploration sci-fi")
    top_n: int = Field(default=6, ge=1, le=20)
    user_id: Optional[int] = Field(default=None, example=42)


class ItemResult(BaseModel):
    title: str
    avg_rating: float
    rating_count: int
    content_score: float
    collab_score: float
    hybrid_score: float
    # movie-specific
    year: Optional[str] = None
    genres: Optional[str] = None
    # book-specific
    author: Optional[str] = None


class RecommendResponse(BaseModel):
    query: str
    movies: list[ItemResult]
    books: list[ItemResult]


class ModelInfo(BaseModel):
    movie: dict
    book: dict

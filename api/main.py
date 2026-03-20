"""
main.py — FastAPI application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.recommend.schemas import RecommendRequest, RecommendResponse, ModelInfo
from api.recommend.service import recommender

app = FastAPI(
    title="Hybrid Recommender API",
    description="Content-based + Collaborative Filtering for movies & books",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model/info", response_model=ModelInfo)
def model_info():
    return recommender.model_info()


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    try:
        movies = recommender.recommend(
            query=req.query,
            item_type="movie",
            top_n=req.top_n,
            user_id=req.user_id,
        )
        books = recommender.recommend(
            query=req.query,
            item_type="book",
            top_n=req.top_n,
            user_id=req.user_id,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RecommendResponse(query=req.query, movies=movies, books=books)

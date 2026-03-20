"""
tests/test_api.py
─────────────────
Run with: pytest tests/ -v
Requires models to be trained first (scripts/train.py).
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_model_info():
    res = client.get("/model/info")
    assert res.status_code == 200
    data = res.json()
    assert "movie" in data
    assert "book" in data


def test_recommend_basic():
    res = client.post("/recommend", json={"query": "space adventure sci-fi", "top_n": 4})
    assert res.status_code == 200
    body = res.json()
    assert body["query"] == "space adventure sci-fi"
    assert len(body["movies"]) == 4
    assert len(body["books"]) == 4


def test_recommend_scores_in_range():
    res = client.post("/recommend", json={"query": "romantic comedy", "top_n": 3})
    assert res.status_code == 200
    for item in res.json()["movies"] + res.json()["books"]:
        assert 0.0 <= item["hybrid_score"] <= 1.0
        assert 0.0 <= item["content_score"] <= 1.0
        assert 0.0 <= item["collab_score"] <= 1.0


def test_recommend_sorted_by_hybrid():
    res = client.post("/recommend", json={"query": "thriller mystery", "top_n": 6})
    movies = res.json()["movies"]
    scores = [m["hybrid_score"] for m in movies]
    assert scores == sorted(scores, reverse=True)


def test_recommend_empty_query():
    res = client.post("/recommend", json={"query": "a", "top_n": 4})
    assert res.status_code == 422  # pydantic min_length=2


def test_recommend_top_n_limit():
    res = client.post("/recommend", json={"query": "horror", "top_n": 21})
    assert res.status_code == 422  # max top_n is 20

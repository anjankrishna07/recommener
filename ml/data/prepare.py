"""
prepare_data.py
───────────────
Downloads and preprocesses movie and book datasets.

Movies : MovieLens ml-latest-small (100k ratings, 9k movies) — no login needed
Books  : Goodreads books CSV (Kaggle) — place manually at data/books_raw.csv
         Download: https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks
"""

import os
import zipfile
import urllib.request
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from pathlib import Path

nltk.download("stopwords", quiet=True)
STOP = set(stopwords.words("english"))

DATA_DIR = Path(__file__).parent
DATA_DIR.mkdir(exist_ok=True)

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"


# ─── Helpers ───────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    tokens = text.lower().split()
    tokens = [t for t in tokens if t.isalpha() and t not in STOP]
    return " ".join(tokens)


def download_movielens():
    zip_path = DATA_DIR / "ml-latest-small.zip"
    if not zip_path.exists():
        print("Downloading MovieLens small dataset…")
        urllib.request.urlretrieve(MOVIELENS_URL, zip_path)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(DATA_DIR)
    print("MovieLens downloaded ✓")


# ─── Movies ────────────────────────────────────────────────────────────────────

def prepare_movies():
    download_movielens()

    ml_dir = DATA_DIR / "ml-latest-small"
    movies_df = pd.read_csv(ml_dir / "movies.csv")   # movieId, title, genres
    ratings_df = pd.read_csv(ml_dir / "ratings.csv") # userId, movieId, rating

    # Parse year from title
    movies_df["year"] = movies_df["title"].str.extract(r"\((\d{4})\)$")
    movies_df["title_clean"] = movies_df["title"].str.replace(r"\s*\(\d{4}\)$", "", regex=True)

    # Genre text for content-based
    movies_df["genres_clean"] = movies_df["genres"].str.replace("|", " ", regex=False)
    movies_df["content"] = (
        movies_df["title_clean"] + " " + movies_df["genres_clean"]
    ).apply(clean_text)

    # Aggregate ratings for collaborative
    avg_ratings = ratings_df.groupby("movieId").agg(
        avg_rating=("rating", "mean"),
        rating_count=("rating", "count"),
    ).reset_index()

    movies_df = movies_df.merge(avg_ratings, on="movieId", how="left")
    movies_df["avg_rating"] = movies_df["avg_rating"].fillna(0)
    movies_df["rating_count"] = movies_df["rating_count"].fillna(0)

    # Keep items with enough ratings
    movies_df = movies_df[movies_df["rating_count"] >= 5].reset_index(drop=True)

    out = movies_df[["movieId", "title_clean", "year", "genres_clean", "content",
                      "avg_rating", "rating_count"]].rename(columns={"title_clean": "title"})
    out.to_csv(DATA_DIR / "movies.csv", index=False)

    # Save ratings for collaborative model
    ratings_df = ratings_df[ratings_df["movieId"].isin(out["movieId"])]
    ratings_df.to_csv(DATA_DIR / "movie_ratings.csv", index=False)

    print(f"Movies prepared: {len(out)} items ✓")
    return out, ratings_df


# ─── Books ─────────────────────────────────────────────────────────────────────

def prepare_books():
    raw_path = DATA_DIR / "books_raw.csv"

    if not raw_path.exists():
        # Fallback: generate a small synthetic dataset so the pipeline still runs
        print("⚠️  books_raw.csv not found — generating synthetic fallback dataset.")
        print("    For the full dataset, download from:")
        print("    https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks")
        _generate_synthetic_books(raw_path)

    df = pd.read_csv(raw_path, on_bad_lines="skip")

    # Normalise column names (Kaggle dataset uses these)
    col_map = {
        "bookID": "bookId",
        "title": "title",
        "authors": "author",
        "average_rating": "avg_rating",
        "ratings_count": "rating_count",
        "  num_pages": "pages",
        "num_pages": "pages",
        "language_code": "language",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    if "bookId" not in df.columns:
        df["bookId"] = range(len(df))

    df = df[df.get("language", "eng") == "eng"] if "language" in df.columns else df
    df["avg_rating"] = pd.to_numeric(df.get("avg_rating", 0), errors="coerce").fillna(0)
    df["rating_count"] = pd.to_numeric(df.get("rating_count", 0), errors="coerce").fillna(0)
    df = df[df["rating_count"] >= 5]

    df["content"] = (df["title"].astype(str) + " " + df.get("author", "").astype(str)).apply(clean_text)

    out = df[["bookId", "title", "author", "avg_rating", "rating_count", "content"]].reset_index(drop=True)
    out.to_csv(DATA_DIR / "books.csv", index=False)
    print(f"Books prepared: {len(out)} items ✓")
    return out


def _generate_synthetic_books(path):
    """Minimal synthetic book dataset for testing the pipeline."""
    rows = [
        ("The Hobbit", "J.R.R. Tolkien", 4.28, 2800000),
        ("Dune", "Frank Herbert", 4.23, 900000),
        ("1984", "George Orwell", 4.19, 3500000),
        ("Sapiens", "Yuval Noah Harari", 4.40, 700000),
        ("The Name of the Wind", "Patrick Rothfuss", 4.54, 650000),
        ("Project Hail Mary", "Andy Weir", 4.53, 400000),
        ("Thinking Fast and Slow", "Daniel Kahneman", 4.18, 500000),
        ("The Martian", "Andy Weir", 4.40, 750000),
        ("Ender's Game", "Orson Scott Card", 4.30, 900000),
        ("The Great Gatsby", "F. Scott Fitzgerald", 3.91, 4000000),
        ("Educated", "Tara Westover", 4.47, 700000),
        ("Gone Girl", "Gillian Flynn", 3.85, 1200000),
        ("The Alchemist", "Paulo Coelho", 3.88, 2500000),
        ("Atomic Habits", "James Clear", 4.37, 600000),
        ("A Brief History of Time", "Stephen Hawking", 4.22, 500000),
        ("The Da Vinci Code", "Dan Brown", 3.73, 2000000),
        ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", 4.47, 8000000),
        ("The Hunger Games", "Suzanne Collins", 4.33, 6000000),
        ("To Kill a Mockingbird", "Harper Lee", 4.27, 5000000),
        ("Brave New World", "Aldous Huxley", 3.99, 1500000),
    ]
    df = pd.DataFrame(rows, columns=["title", "author", "avg_rating", "rating_count"])
    df["bookId"] = range(len(df))
    df.to_csv(path, index=False)


# ─── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Preparing datasets ===")
    prepare_movies()
    prepare_books()
    print("\n✅ Data preparation complete. Files saved to backend/data/")

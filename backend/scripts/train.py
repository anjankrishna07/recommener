"""
train.py
────────
Trains and serialises the hybrid recommendation models.

Models trained:
  1. Content-Based  — TF-IDF vectoriser + cosine similarity matrix
  2. Collaborative  — SVD (Truncated) on user-item rating matrix
  3. Hybrid         — weighted blender (tunable alpha)

Run:
    python scripts/train.py
"""

import time
import joblib
import mlflow
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

DATA_DIR   = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

ALPHA = 0.6   # weight for content-based score (1-ALPHA for collaborative)
SVD_K = 50    # latent factors


# ══════════════════════════════════════════════════════════════════════════════
# 1. CONTENT-BASED MODEL
# ══════════════════════════════════════════════════════════════════════════════

def train_content_model(df: pd.DataFrame, item_type: str):
    """
    Fits a TF-IDF vectoriser on item content text and computes
    a cosine similarity matrix.

    Returns:
        tfidf      : fitted TfidfVectorizer
        sim_matrix : (n_items x n_items) cosine similarity array
    """
    print(f"  Training content model for {item_type}s…")
    t0 = time.time()

    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
    )
    tfidf_matrix = tfidf.fit_transform(df["content"].fillna(""))
    sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    elapsed = time.time() - t0
    print(f"    ✓ {item_type} TF-IDF shape: {tfidf_matrix.shape} ({elapsed:.1f}s)")
    return tfidf, tfidf_matrix, sim_matrix


# ══════════════════════════════════════════════════════════════════════════════
# 2. COLLABORATIVE FILTERING MODEL  (SVD)
# ══════════════════════════════════════════════════════════════════════════════

def train_collab_model(ratings_df: pd.DataFrame, item_col: str):
    """
    Builds a user-item matrix and decomposes it with truncated SVD.

    Returns:
        predicted_ratings : (n_users x n_items) dense predicted matrix
        user_index        : {userId -> row index}
        item_index        : {itemId -> col index}
        rmse              : float
    """
    print(f"  Training collaborative model…")
    t0 = time.time()

    # Encode IDs to sequential indices
    users = ratings_df["userId"].unique()
    items = ratings_df[item_col].unique()
    user_idx = {u: i for i, u in enumerate(users)}
    item_idx = {it: i for i, it in enumerate(items)}

    n_users, n_items = len(users), len(items)

    # Build sparse user-item matrix
    row = ratings_df["userId"].map(user_idx)
    col = ratings_df[item_col].map(item_idx)
    val = ratings_df["rating"].astype(float)
    sparse_mat = csr_matrix((val, (row, col)), shape=(n_users, n_items))

    # Mean-center by user
    user_ratings_mean = np.array(sparse_mat.mean(axis=1)).flatten()
    mat_demeaned = sparse_mat - csr_matrix(
        np.outer(user_ratings_mean, np.ones(n_items))
    )

    # SVD
    k = min(SVD_K, min(n_users, n_items) - 1)
    U, sigma, Vt = svds(mat_demeaned.toarray(), k=k)
    sigma_diag = np.diag(sigma)
    predicted = user_ratings_mean[:, np.newaxis] + U @ sigma_diag @ Vt

    # RMSE on observed entries
    observed_mask = sparse_mat.toarray() > 0
    rmse = np.sqrt(mean_squared_error(
        sparse_mat.toarray()[observed_mask],
        predicted[observed_mask]
    ))

    elapsed = time.time() - t0
    print(f"    ✓ SVD k={k}, n_users={n_users}, n_items={n_items}, RMSE={rmse:.4f} ({elapsed:.1f}s)")
    return predicted, user_idx, item_idx, float(rmse)


# ══════════════════════════════════════════════════════════════════════════════
# 3. HYBRID SCORER
# ══════════════════════════════════════════════════════════════════════════════

def compute_popularity_scores(df: pd.DataFrame) -> np.ndarray:
    """Normalised Bayesian average rating for cold-start fallback."""
    C = df["avg_rating"].mean()
    m = df["rating_count"].quantile(0.25)
    scores = (
        (df["rating_count"] / (df["rating_count"] + m)) * df["avg_rating"]
        + (m / (df["rating_count"] + m)) * C
    )
    mn, mx = scores.min(), scores.max()
    return ((scores - mn) / (mx - mn + 1e-8)).values


# ══════════════════════════════════════════════════════════════════════════════
# 4. TRAIN & SAVE EVERYTHING
# ══════════════════════════════════════════════════════════════════════════════

def train_and_save(item_type: str):
    """Train full pipeline for movies or books and serialise."""

    # ── Load data ──────────────────────────────────────────────────────────
    items_df  = pd.read_csv(DATA_DIR / f"{item_type}s.csv")
    id_col    = "movieId" if item_type == "movie" else "bookId"

    with mlflow.start_run(run_name=f"{item_type}_hybrid"):
        mlflow.log_param("item_type",  item_type)
        mlflow.log_param("alpha",      ALPHA)
        mlflow.log_param("svd_k",      SVD_K)
        mlflow.log_param("n_items",    len(items_df))

        # ── Content model ──────────────────────────────────────────────────
        tfidf, tfidf_matrix, sim_matrix = train_content_model(items_df, item_type)

        # ── Collaborative model ────────────────────────────────────────────
        collab_data = None
        collab_rmse = None

        ratings_path = DATA_DIR / f"{item_type}_ratings.csv"
        if ratings_path.exists():
            ratings_df  = pd.read_csv(ratings_path)
            predicted_ratings, user_idx, item_idx, collab_rmse = train_collab_model(
                ratings_df, id_col
            )
            collab_data = {
                "predicted_ratings": predicted_ratings,
                "user_index": user_idx,
                "item_index": item_idx,
            }
            mlflow.log_metric("collab_rmse", collab_rmse)
        else:
            print(f"  ⚠ No ratings file found for {item_type}s — collab model skipped.")

        # ── Popularity scores (cold-start) ─────────────────────────────────
        pop_scores = compute_popularity_scores(items_df)

        # ── Serialise ──────────────────────────────────────────────────────
        bundle = {
            "item_type":    item_type,
            "items_df":     items_df,
            "id_col":       id_col,
            "tfidf":        tfidf,
            "tfidf_matrix": tfidf_matrix,
            "sim_matrix":   sim_matrix,
            "collab":       collab_data,
            "pop_scores":   pop_scores,
            "alpha":        ALPHA,
        }

        out_path = MODELS_DIR / f"{item_type}_model.joblib"
        joblib.dump(bundle, out_path, compress=3)
        mlflow.log_artifact(str(out_path))

        n_vocab = len(tfidf.vocabulary_)
        mlflow.log_metric("vocab_size", n_vocab)

        print(f"    ✓ Saved → {out_path}")
        print(f"    Vocab size : {n_vocab}")
        if collab_rmse:
            print(f"    Collab RMSE: {collab_rmse:.4f}")


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mlflow.set_experiment("hybrid-recommender")
    print("=== Training models ===\n")

    print("── MOVIES ──")
    train_and_save("movie")

    print("\n── BOOKS ──")
    train_and_save("book")

    print("\n✅ Training complete. Models saved to backend/models/")
    print("   View experiments: mlflow ui --port 5000")

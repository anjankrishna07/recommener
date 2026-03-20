"""
recommender.py
──────────────
Hybrid recommendation engine used at inference time.

Strategy
────────
Given a free-text user query:

  1. Content Score  — TF-IDF transform the query → cosine similarity
                      against every item in the catalogue.

  2. Collab Score   — If a userId is supplied, look up that user's
                      predicted ratings from the SVD matrix and normalise.
                      Otherwise fall back to popularity (Bayesian avg).

  3. Hybrid Score   — alpha * content + (1-alpha) * collab/popularity

Items are ranked by hybrid score and the top-N are returned.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

MODELS_DIR = Path(__file__).parent.parent.parent / "ml" / "artifacts"


class HybridRecommender:
    def __init__(self):
        self._bundles: dict = {}

    def _load(self, item_type: str) -> dict:
        if item_type not in self._bundles:
            path = MODELS_DIR / f"{item_type}_model.joblib"
            if not path.exists():
                raise FileNotFoundError(
                    f"Model not found: {path}. Run scripts/train.py first."
                )
            self._bundles[item_type] = joblib.load(path)
        return self._bundles[item_type]

    # ── public API ────────────────────────────────────────────────────────────

    def recommend(
        self,
        query: str,
        item_type: str,       # "movie" | "book"
        top_n: int = 6,
        user_id: int = None,
    ) -> list[dict]:
        """
        Returns top_n recommendations for the given query.

        Parameters
        ----------
        query     : free-text user interest string
        item_type : "movie" or "book"
        top_n     : number of results to return
        user_id   : optional — activates collaborative component

        Returns
        -------
        List of dicts with item metadata + scores.
        """
        bundle = self._load(item_type)

        content_scores = self._content_score(query, bundle)
        collab_scores  = self._collab_score(user_id, bundle)

        alpha = bundle["alpha"]
        hybrid = alpha * content_scores + (1 - alpha) * collab_scores

        df = bundle["items_df"].copy()
        df["content_score"] = content_scores
        df["collab_score"]  = collab_scores
        df["hybrid_score"]  = hybrid

        top = df.nlargest(top_n, "hybrid_score")
        return self._format(top, item_type)

    # ── private ───────────────────────────────────────────────────────────────

    def _content_score(self, query: str, bundle: dict) -> np.ndarray:
        tfidf        = bundle["tfidf"]
        tfidf_matrix = bundle["tfidf_matrix"]

        query_vec = tfidf.transform([query])
        scores    = cosine_similarity(query_vec, tfidf_matrix).flatten()

        # Normalise to [0, 1]
        mn, mx = scores.min(), scores.max()
        return (scores - mn) / (mx - mn + 1e-8)

    def _collab_score(self, user_id, bundle: dict) -> np.ndarray:
        collab = bundle["collab"]

        if collab is not None and user_id is not None:
            user_idx    = collab["user_index"]
            item_idx    = collab["item_index"]
            predicted   = collab["predicted_ratings"]
            id_col      = bundle["id_col"]
            items_df    = bundle["items_df"]

            if user_id in user_idx:
                u_row   = user_idx[user_id]
                u_preds = predicted[u_row]          # shape (n_collab_items,)

                # Map back to catalogue order
                scores  = np.zeros(len(items_df))
                for i, item_id in enumerate(items_df[id_col]):
                    if item_id in item_idx:
                        scores[i] = u_preds[item_idx[item_id]]

                mn, mx = scores.min(), scores.max()
                return (scores - mn) / (mx - mn + 1e-8)

        # Cold-start fallback — popularity
        return bundle["pop_scores"]

    def _format(self, df: pd.DataFrame, item_type: str) -> list[dict]:
        records = []
        for _, row in df.iterrows():
            base = {
                "title":         row["title"],
                "avg_rating":    round(float(row.get("avg_rating", 0)), 2),
                "rating_count":  int(row.get("rating_count", 0)),
                "content_score": round(float(row["content_score"]), 4),
                "collab_score":  round(float(row["collab_score"]), 4),
                "hybrid_score":  round(float(row["hybrid_score"]), 4),
            }
            if item_type == "movie":
                base["year"]   = str(row.get("year", ""))
                base["genres"] = str(row.get("genres_clean", ""))
            else:
                base["author"] = str(row.get("author", ""))
            records.append(base)
        return records

    def model_info(self) -> dict:
        info = {}
        for item_type in ("movie", "book"):
            try:
                b = self._load(item_type)
                info[item_type] = {
                    "n_items":    len(b["items_df"]),
                    "vocab_size": len(b["tfidf"].vocabulary_),
                    "alpha":      b["alpha"],
                    "has_collab": b["collab"] is not None,
                }
            except FileNotFoundError:
                info[item_type] = {"error": "model not trained yet"}
        return info


# Singleton instance
recommender = HybridRecommender()
